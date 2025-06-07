# <<07-JUN-2025:23:05>> - Integrated ui_helpers, replaced inline spinner & selector logic.
#               Imports helpers and uses wait_for_selector_flexible and other
#               utilities. Maintained tab indentation and logging.
# <<07-JUN-2025:22:45>> - Initial modularization of playwright_runner.py

from __future__ import annotations

import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional

from dotenv import load_dotenv
from playwright.async_api import Page, Browser, async_playwright

from utils.logging import debug_log, capture_screenshot, log_html_to_file
from oracle.login_steps import run_oracle_login_steps
from oracle.navigation import (
	load_ui_map,
	find_page_id_by_label,
	navigate_to as async_navigate_to,
)

# Newly extracted helpers
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
# Environment helpers
# ----------------------------------------------------------------------------

def _load_env() -> bool:
	"""Load environment variables using dotenv search and resolve HEADLESS_MODE.

	Uses `find_dotenv()` so the runner works even when the current working
	directory is inside nested test folders. Defaults to headless **true** when
	no variable is found.
	"""
	from dotenv import find_dotenv

	dotenv_path = find_dotenv(usecwd=True)
	if dotenv_path:
		load_dotenv(dotenv_path, override=False)
		debug_log(f"Loaded .env from {dotenv_path}")
	else:
		debug_log("No .env file found via find_dotenv; relying on process envs")

	return os.getenv("HEADLESS_MODE", "true").lower() == "true"


# ----------------------------------------------------------------------------
# Browser helpers
# ----------------------------------------------------------------------------

async def _new_browser_context(headless: bool) -> Tuple[Browser, Page]:
	"""Launch a fresh Chromium browser/context/page with given headless flag."""
	p = await async_playwright().start()
	browser = await p.chromium.launch(headless=headless)
	context = await browser.new_context()
	page = await context.new_page()
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

	headless_mode = _load_env()
	debug_log(f"Headless mode = {headless_mode}")

	try:
		if page is None or browser is None:
			browser, page = await _new_browser_context(headless=headless_mode)

		if not already_logged_in:
			await run_oracle_login_steps(page, login_url, username, password, session_id, page.url)
			already_logged_in = True
			await wait_for_spinner(page)

			# Expand nav panel early for reliable selectability
			await expand_nav_panel_if_collapsed(page)

			if target_label:
				ui_map = load_ui_map("oracle/ui_map.jsonl")
				page_id = find_page_id_by_label(ui_map, target_label, parent_label)
				if page_id:
					await async_navigate_to(page, "oracle/ui_map.jsonl", page_id)
					await wait_for_spinner(page)

		# Execute scripted steps
		for idx, step in enumerate(steps, 1):
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
	action   = step.get("action")
	selector = step.get("selector")
	value    = step.get("value")
	context  = step.get("context")
	row_name = step.get("rowName")

	debug_log(f"Step {idx}: {action} sel={selector} val={value} ctx={context} row={row_name}")

	try:
		if action == "goto":
			await page.goto(value)
			await wait_for_spinner(page)
		elif action == "fill":
			await wait_for_selector_flexible(page, selector, context_section=context)
			await page.fill(selector, value)
		elif action == "click":
			if "Export to Excel" in selector or "export-to-excel" in selector:
				await click_export_to_excel(page)
			else:
				await wait_for_selector_flexible(page, selector, context_section=context)
				await page.click(selector)
		elif action == "wait_for_selector":
			await wait_for_selector_flexible(page, selector, context_section=context, timeout=step.get("timeout", 30000))
		elif action == "wait_for_timeout":
			await page.wait_for_timeout(int(value))
		elif action == "assert":
			content = await page.content()
			if value not in content:
				raise AssertionError(f"Assertion failed: '{value}' not found")
		else:
			debug_log(f"Unsupported action {action}")

		await capture_screenshot(page, session_id, f"{ts}_step_{idx}_{action}", idx)
		html = await page.content()
		await log_html_to_file(idx, html, session_id)

	except Exception as exc:
		debug_log(f"Step {idx} failed: {exc}")
		await capture_screenshot(page, session_id, f"{ts}_error_{idx}", idx)
		html = await page.content()
		await log_html_to_file(f"{idx}_error", html, session_id)
		raise
