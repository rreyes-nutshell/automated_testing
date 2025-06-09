# <<08-JUN-2025:02:11>> - Merged selector support and enforced debug_log on all functions

from __future__ import annotations

import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional

from dotenv import load_dotenv
from playwright.async_api import Page, Browser, async_playwright

from utils.logging import debug_log, capture_screenshot, log_html_to_file, load_env
from utils.selector_resolver import get_selector
from utils.step_interpolation import interpolate_step_vars
from oracle.login_steps import run_oracle_login_steps
from oracle.navigation import (
	load_ui_map,
	find_page_id_by_label,
	navigate_to as async_navigate_to,
)

from services.ui_helpers import (
	wait_for_spinner,
	expand_nav_panel_if_collapsed,
	click_menu_item_by_text,
	toggle_checkbox_under_section,
	check_checkbox_by_role,
	click_export_to_excel,
	wait_for_selector_flexible,
)

# ----------------------------------------------------------------------------
# Browser helpers
# ----------------------------------------------------------------------------

# <<08-JUN-2025:19:39>> Removed get_ui_db_connection in favor of shared db_utils routines

async def _new_browser_context(headless: bool) -> Tuple[Browser, Page]:
	"""Launch a fresh Chromium browser/context/page with given headless flag."""
	debug_log("Entered _new_browser_context")
	load_env()
	p = await async_playwright().start()
	browser = await p.chromium.launch(headless=headless)
	context = await browser.new_context()
	page = await context.new_page()
	debug_log(f"New browser context created: headless={headless}, page={page.url}")
	debug_log("Exited _new_browser_context")
	return browser, page


# ----------------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------------

async def run_browser_script(
	*,
	steps: List[Dict],
	session_id: str,
	login_url: str,
	username: str,
	password: str,
	preview_mode: bool = False,
	target_label: Optional[str] = None,
	parent_label: Optional[str] = None,
	page: Optional[Page] = None,
	browser: Optional[Browser] = None,
	already_logged_in: bool = False,
) -> Tuple[Optional[Page], Optional[Browser], bool]:
	"""Executes a series of Playwright steps using helpers for resilience."""
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	debug_log("Entered run_browser_script")

	if preview_mode:
		for idx, step in enumerate(steps, 1):
			debug_log(f"[Preview] Step {idx}: {step}")
		return None, None, False

	headless_mode = load_env()
	debug_log(f"Headless mode = {headless_mode}")

	try:
		if page is None or browser is None:
			browser, page = await _new_browser_context(headless=headless_mode)

		if not already_logged_in:
			await run_oracle_login_steps(page, login_url, username, password, session_id, page.url)
			already_logged_in = True
			await wait_for_spinner(page)
			await expand_nav_panel_if_collapsed(page)

			if target_label:
				ui_map = load_ui_map("oracle/ui_map.jsonl")
				page_id = find_page_id_by_label(ui_map, target_label, parent_label)
				if page_id:
					await async_navigate_to(page, "oracle/ui_map.jsonl", page_id)
					await wait_for_spinner(page)

		# Execute scripted steps
		context_vars = {"login_url": login_url, "username": username, "password": password}
		login_only_keys = {"username_input", "password_input", "sign_in_button", "login_error_banner"}
		navigation_keys = {"navigator_button", "hamburger_icon"}
		for idx, step in enumerate(steps, 1):
			step = interpolate_step_vars(step, context_vars)

			if already_logged_in and step.get("action") == "goto" and step.get("target") == login_url:
				debug_log(f"Skipping redundant goto step {idx} to login_url since already_logged_in is True")
				continue

			if already_logged_in and step.get("selector") in login_only_keys:
				debug_log(f"Skipping login-only selector '{step['selector']}' since already_logged_in is True")
				continue

			if step.get("selector") in navigation_keys:
				debug_log(f"🔍 Preparing to interact with nav item: {step['selector']}")
				await capture_screenshot(page, session_id, f"{timestamp}_before_nav_{idx}", idx)

			await _execute_step(step, page, session_id, timestamp, idx)

		return page, browser, already_logged_in

	except Exception as exc:
		debug_log(f"Runner exception: {exc}")
		return None, None, False
	finally:
		debug_log("Exited run_browser_script")


# ----------------------------------------------------------------------------
# Internal helpers
# ----------------------------------------------------------------------------

async def _execute_step(step: Dict, page: Page, session_id: str, ts: str, idx: int):
	"""Execute a single scripted action leveraging ui_helpers."""
	debug_log("Entered _execute_step")
	action   = step.get("action")
	selector = step.get("selector")
	value    = step.get("value")
	context  = step.get("context")
	row_name = step.get("rowName")

	resolved_selector = get_selector(selector) if selector else None
	debug_log(f"Step {idx}: {action} sel={resolved_selector} val={value} ctx={context} row={row_name}")

	try:
		if action == "goto":
			await page.goto(value)
			await wait_for_spinner(page)
		elif action == "fill" and resolved_selector:
			await wait_for_selector_flexible(page, resolved_selector, context_section=context)
			await page.fill(resolved_selector, value)
		elif action == "click" and resolved_selector:
			if "Export to Excel" in resolved_selector or "export-to-excel" in resolved_selector:
				await click_export_to_excel(page)
			else:
				await wait_for_selector_flexible(page, resolved_selector, context_section=context)
				await page.click(resolved_selector)
		elif action == "wait_for_selector" and resolved_selector:
			# await wait_for_selector_flexible(page, resolved_selector, context_section=context, timeout=step.get("timeout", 30000))
			await wait_for_selector_flexible(page, resolved_selector, context_section=context, timeout=step.get("timeout", 5000))
		elif action == "wait_for_timeout":
			await page.wait_for_timeout(int(value))
		elif action == "assert":
			content = await page.content()
			if value not in content:
				raise AssertionError(f"Assertion failed: '{value}' not found")
		else:
			debug_log(f"Unsupported action {action}")

		suffix = f"{ts}_step_{idx}_{action}"
		await capture_screenshot(page, session_id, suffix, idx)
		html = await page.content()
		await log_html_to_file(idx, html, session_id)

	except Exception as exc:
		debug_log(f"Step {idx} failed: {exc}")
		await capture_screenshot(page, session_id, f"{ts}_error_{idx}", idx)
		html = await page.content()
		await log_html_to_file(f"{idx}_error", html, session_id)
		raise
	finally:
		debug_log("Exited _execute_step")
