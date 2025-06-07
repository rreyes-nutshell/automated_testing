# <<07-JUN-2025:22:59>> - Added missing helpers (check_checkbox_by_role, click_export_to_excel, wait_for_selector_flexible)
# <<07-JUN-2025:22:50>> - Initial extraction of UI helper utilities from Playwright runner
#               Provides reusable async helpers for Oracle Cloud UI automation.
#               All functions include debug_log entry/exit and use tab indentation.

from __future__ import annotations

from typing import Optional

from playwright.async_api import Page, Download

from utils.logging import debug_log

# ----------------------------------------------------------------------------
# Generic helper utilities (Oracle‑centric, but broadly usable)
# ----------------------------------------------------------------------------

DEFAULT_TIMEOUT = 30_000  # 30 seconds

# ----------------------------------------------------------------------------
# Spinner / panel helpers
# ----------------------------------------------------------------------------

async def wait_for_spinner(page: Page, timeout: int = DEFAULT_TIMEOUT):
	"""Wait until Oracle's progress spinner disappears."""
	debug_log("Entered wait_for_spinner")
	try:
		await page.wait_for_selector("css=div[role='progressbar']", state="hidden", timeout=timeout)
	finally:
		debug_log("Exited wait_for_spinner")


async def expand_nav_panel_if_collapsed(page: Page, timeout: int = DEFAULT_TIMEOUT):
	"""Ensure the left navigation panel is expanded."""
	debug_log("Entered expand_nav_panel_if_collapsed")
	nav_toggle = page.locator("css=button[data-test='o-header-nav-toggle']")
	if nav_toggle and await nav_toggle.is_visible():
		await nav_toggle.click(timeout=timeout)
		await wait_for_spinner(page, timeout)
		debug_log("Navigation panel expanded")
	else:
		debug_log("Navigation panel already visible or toggle not found")
	debug_log("Exited expand_nav_panel_if_collapsed")

# ----------------------------------------------------------------------------
# Checkbox helpers
# ----------------------------------------------------------------------------

async def toggle_checkbox_under_section(
	page: Page,
	section_label: str,
	checkbox_label: str,
	selected: bool = True,
	timeout: int = DEFAULT_TIMEOUT,
):
	"""Toggle a checkbox nested within a collapsible section."""
	debug_log(f"Entered toggle_checkbox_under_section — {section_label} > {checkbox_label} -> {selected}")

	section_sel = f"role=button[name='{section_label}']"
	if await page.locator(section_sel).get_attribute("aria-expanded") == "false":
		await page.click(section_sel, timeout=timeout)
		await wait_for_spinner(page)

	row_sel = f"role=row >> text='{checkbox_label}'"
	checkbox = page.locator(row_sel).locator("css=input[type='checkbox']")
	if await checkbox.is_checked() != selected:
		await checkbox.click(timeout=timeout)
		await wait_for_spinner(page)
		debug_log(f"Checkbox '{checkbox_label}' now {selected}")
	else:
		debug_log(f"Checkbox '{checkbox_label}' already {selected}")
	debug_log("Exited toggle_checkbox_under_section")


async def check_checkbox_by_role(
	page: Page,
	label: str,
	section: Optional[str] = None,
	selected: bool = True,
	timeout: int = DEFAULT_TIMEOUT,
):
	"""Check/uncheck a checkbox located by ARIA role and label."""
	debug_log(f"Entered check_checkbox_by_role label='{label}' section='{section}' -> {selected}")
	locator = (
		page.get_by_role("row", name=section).get_by_label(label)
		if section else page.get_by_label(label).first
	)
	if selected:
		await locator.check(timeout=timeout)
	else:
		await locator.uncheck(timeout=timeout)
	debug_log("Exited check_checkbox_by_role")

# ----------------------------------------------------------------------------
# Menu / click helpers
# ----------------------------------------------------------------------------

async def click_menu_item_by_text(page: Page, menu_text: str, timeout: int = DEFAULT_TIMEOUT):
	"""Click a menu item by visible text."""
	debug_log(f"Entered click_menu_item_by_text — '{menu_text}'")
	await page.click(f"role=menuitem >> text='{menu_text}'", timeout=timeout)
	await wait_for_spinner(page)
	debug_log("Exited click_menu_item_by_text")


async def click_export_to_excel(page: Page, timeout: int = DEFAULT_TIMEOUT) -> Download:
	"""Click 'Export to Excel' button and return the Download object."""
	debug_log("Entered click_export_to_excel")
	async with page.expect_download() as dl_info:
		await page.get_by_role("button", name="Export to Excel").first.click(timeout=timeout)
		download = dl_info.value
	debug_log("Download initiated")
	await wait_for_spinner(page)
	debug_log("Exited click_export_to_excel")
	return download

# ----------------------------------------------------------------------------
# Flexible selector wait helper
# ----------------------------------------------------------------------------

async def wait_for_selector_flexible(
	page: Page,
	selector: str,
	context_section: Optional[str] = None,
	timeout: int = DEFAULT_TIMEOUT,
):
	"""Wait for a selector with a fallback heuristics for nav-link / checkbox slugs."""
	debug_log(f"Entered wait_for_selector_flexible sel='{selector}' ctx='{context_section}'")
	try:
		await page.wait_for_selector(selector, timeout=timeout)
	except Exception as primary_err:
		debug_log(f"Primary wait failed: {primary_err}")
		if selector.startswith("css="):
			raw_css = selector.split("=", 1)[1]
			label = raw_css.split(".")[-1].replace("-", " ").title()
			if "export" in raw_css:
				await page.get_by_role("button", name="Export to Excel").first.wait_for(state="visible", timeout=timeout)
			else:
				cb_locator = (
					page.get_by_role("row", name=context_section).get_by_role("checkbox", name=label)
					if context_section else page.get_by_role("checkbox", name=label).first
				)
				await cb_locator.wait_for(state="visible", timeout=timeout)
	finally:
		debug_log("Exited wait_for_selector_flexible")
