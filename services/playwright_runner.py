# <<31-MAY-2025:16:28>> - Merged cookie-based persistence and DOM extraction into existing path_crawler version
# playwright_runner.py
# <<02-JUN-2025:21:50>> – Added import for new helper module

# from playwright.async_api import async_playwright
# from utils.logging import debug_log, capture_screenshot, log_html_to_file
# from utils.selectors import ensure_escaped_selector
# from datetime import datetime
# from oracle.login_steps import run_oracle_login_steps
# from oracle.locators import LOCATORS
# from oracle.navigation import load_ui_map, find_page_id_by_label, navigate_to as async_navigate_to
# from services.browser_service import browser_service
# from dotenv import load_dotenv
# import os
# import re


# # <<31-MAY-2025:18:30>> – Modified return logic so caller can keep browser open for crawler
# async def run_browser_script(
#     *,
#     steps: list[dict],
#     session_id: str,
#     login_url: str,
#     username: str,
#     password: str,
#     preview_mode: bool = False,
#     target_label: str = None,
#     parent_label: str = None,
#     page=None,
#     browser=None,
#     already_logged_in: bool = False
# ):
#     """
#     If page/browser is passed in, reuse them (so cookies/session persist).
#     Otherwise, create a fresh context, sign in, and run steps.
#     Returns final page HTML at the end of script execution.
#     """

#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     debug_log("Entered run_browser_script")
#     debug_log(f"🧙️ Preview Mode: {preview_mode}")
#     debug_log(f"🧩 Steps to execute: {len(steps)}")
#     debug_log(f"Target label: {target_label}")
#     debug_log(f"Parent label: {parent_label}")

#     if preview_mode:
#         for idx, step in enumerate(steps, 1):
#             debug_log(f"🖟️ [Preview] Step {idx}: {step}")
#         debug_log("🕔️ Skipping execution due to preview mode")
#         debug_log("Exited run_browser_script")
#         return "Preview mode — no browser actions executed."

#     try:
#         load_dotenv()
#         headless_mode = os.getenv("HEADLESS", "true").lower() == "true"

#         # --- Context reuse or fresh launch ---
#         if page is None or browser is None:
#             debug_log("❇️ No existing page/browser -- launching new Playwright context")
#             p = await async_playwright().start()
#             browser = await p.chromium.launch(headless=False)
#             context = await browser.new_context()
#             page = await context.new_page()

#             # Perform login on fresh context
#             if not already_logged_in:
#                 debug_log("🔐 Performing login on fresh context")
#                 await run_oracle_login_steps(page, login_url, username, password, session_id, page.url)
#                 already_logged_in = True
#                 debug_log(f"🔍 Login success — landed on: {page.url}")
                
#                 if target_label:
#                     debug_log(f"🔎 Starting mapped navigation for: {parent_label} → {target_label}")
#                     ui_map = load_ui_map("oracle/ui_map.jsonl")
#                     page_id = find_page_id_by_label(ui_map, target_label, parent_label)
#                     if page_id:
#                         debug_log(f"🔗 Resolved target page ID: {page_id}, executing navigation")
#                         await async_navigate_to(page, "oracle/ui_map.jsonl", page_id)
#                     else:
#                         debug_log(f"⚠️ Unable to resolve navigation to {target_label} under {parent_label}")
#         else:
#             debug_log("✅ Reusing existing page/browser context")
#             # If not yet logged in in this context, perform login
#             if not already_logged_in:
#                 debug_log("🔐 Performing login on existing context")
#                 await run_oracle_login_steps(page, login_url, username, password, session_id, page.url)
#                 already_logged_in = True
#                 debug_log(f"🔍 Login success — landed on: {page.url}")

#         # --- At this point, 'page' is logged in and ready ---
#         for step_num, step in enumerate(steps, 1):
#             action = step.get("action")
#             selector = step.get("selector")
#             value = step.get("value")
#             debug_log(f"🔁 Step {step_num}: {action} - {selector} - {value}")

#             # Ensure selector is properly escaped
#             if selector:
#                 debug_log(f"🔁 Using selector: {selector}")

#                 # <<03-JUN-2025:20:55>> – Handle 'css selector:' prefix by stripping it and escaping
#                 if selector.lower().startswith("css selector:"):
#                     raw_css = selector.split(":", 1)[1].strip()
#                     escaped_css = ensure_escaped_selector(raw_css)
#                     debug_log(f"🔁 Transformed raw '{selector}' to escaped CSS '{escaped_css}'")
#                     selector = f"css={escaped_css}"
#                 # <<end 03-JUN-2025:20:55>>

#                 # <<03-JUN-2025:20:55>> – Skip dot-splitting for raw CSS/XPath selectors
#                 elif selector.startswith(("css=", "xpath=")):
#                     debug_log(f"🔁 Skipping selector simplification for raw locator: {selector}")
#                 else:
#                     # Original dot-splitting logic commented out
#                     pass

#                 if selector == ".button[title='Navigator']":
#                     debug_log(f"🔁 Normalizing selector at step {step_num} to a[title='Navigator']")
#                     selector = "a[title='Navigator']"

#                 if ":contains(" in selector:
#                     match = re.search(r":contains\((.*?)\)", selector)
#                     if match:
#                         label = match.group(1).strip("\"'")
#                         debug_log(f"🔁 Rewriting selector '{selector}' to text='{label}'")
#                         selector = f"text='{label}'"

#                 # Skip login fields if already on home page
#                 if selector in [LOCATORS.get("User ID"), LOCATORS.get("Password")] and "AtkHomePageWelcome" in page.url:
#                     debug_log(f"⚠️ Skipping step {step_num}: Already logged in, selector {selector} not needed.")
#                     continue

#             # Skip unwanted clicks
#             if action == "click" and selector and "show-more" in selector:
#                 debug_log(f"🛑 Skipping step {step_num}: Suppressed 'Show More' click")
#                 continue

#             try:
#                 if action == "goto":
#                     debug_log(f"🔗 GOTO Navigating to: {value}")
#                     await page.goto(value)

#                 elif action == "fill":
#                     debug_log(f"✏️ Filling selector '{selector}' with value '{value}'")
#                     await page.fill(selector, value)

#                 elif action == "click":
#                     # <<04-JUN-2025:07:30>> – For 'Select All', attempt role-based checkbox first before CSS
#                     if selector and selector.startswith("css=") and "select-all" in selector:
#                         label = step.get("label", "Select All")
#                         section = step.get("context")
#                         if section:
#                             debug_log(f"🖱️ Trying role-based click for '{label}' under '{section}' first")
#                             await page.get_by_role("row", name=section).get_by_role("checkbox", name=label).check()
#                             debug_log(f"💼 Role-based checkbox click succeeded for '{label}' under '{section}'")
#                             raise Exception("Skip CSS click for select-all")
#                         else:
#                             debug_log(f"🖱️ Trying role-based click for first checkbox named '{label}' first")
#                             await page.get_by_role("checkbox", name=label).first.check()
#                             debug_log(f"💼 Role-based checkbox click succeeded for first '{label}'")
#                             raise Exception("Skip CSS click for select-all")
#                     # <<end 04-JUN-2025:07:30>>

#                     # <<04-JUN-2025:07:30>> – For 'Export', attempt role-based button click with download wait
#                     if selector and selector.startswith("css=") and "export" in selector:
#                         debug_log(f"🖱️ Trying role-based click for 'Export to Excel' button first")
#                         try:
#                             download_promise = page.wait_for_event("download")
#                             await page.get_by_role("button", name="Export to Excel").first.click()
#                             download = await download_promise
#                             debug_log(f"💼 Download started: {await download.path()}")
#                             raise Exception("Skip CSS click for export")
#                         except Exception as e_btn:
#                             # If controlled skip, re-raise; otherwise, fall back to CSS
#                             if str(e_btn) == "Skip CSS click for export":
#                                 raise
#                             debug_log(f"⚠️ Role-based export click failed: {e_btn}, falling back to CSS")
#                     # <<end 04-JUN-2025:07:30>>

#                     # <<03-JUN-2025:20:55>> – Enhanced click logic for raw CSS selectors with fallback
#                     if selector and selector.startswith("css="):
#                         raw_css = selector.split("=", 1)[1]
#                         escaped_css = ensure_escaped_selector(raw_css)
#                         try:
#                             debug_log(f"🖱️ Clicking escaped CSS: css={escaped_css}")
#                             element = page.locator(f"css={escaped_css}")
#                             await element.scroll_into_view_if_needed()
#                             await element.hover()
#                             await element.click()
#                             await page.wait_for_timeout(5000)
#                             debug_log(f"💼 Clicked selector 'css={escaped_css}'")
#                         except Exception as click_css_error:
#                             debug_log(f"⚠️ CSS click failed: {click_css_error}")
#                             # Derive label and (optional) section for fallback checkbox/button
#                             label = raw_css.split(".")[-1].replace("-", " ").title()
#                             if "export" in raw_css:
#                                 debug_log(f"🔁 Fallback clicking 'Export to Excel' button")
#                                 download_promise = page.wait_for_event("download")
#                                 await page.get_by_role("button", name="Export to Excel").first.click()
#                                 download = await download_promise
#                                 debug_log(f"💼 Download started: {await download.path()}")
#                             else:
#                                 section = step.get("context")
#                                 if section:
#                                     debug_log(f"🔁 Fallback clicking checkbox '{label}' under section '{section}'")
#                                     checkbox = page.get_by_role("row", name=section).get_by_role("checkbox", name=label)
#                                 else:
#                                     debug_log(f"🔁 Fallback clicking first checkbox named '{label}' (no context provided)")
#                                     checkbox = page.get_by_role("checkbox", name=label).first
#                                 await checkbox.check()
#                     else:
#                         # Original click logic
#                         try:
#                             debug_log(f"🖱️ Clicking selector '{selector}'")
#                             element = page.locator(selector)
#                             await element.scroll_into_view_if_needed()
#                             await element.hover()
#                             await element.click()
#                             await page.wait_for_timeout(5000)
#                             debug_log(f"💼 Clicked selector '{selector}'")
#                         except Exception as click_error:
#                             debug_log(f"⚠️ Primary click failed: {click_error}")
#                             if selector and selector.startswith("#"):
#                                 raw_label = selector.split(" > ")[0].strip("#")
#                                 parts = raw_label.replace("_", "-").split("-")
#                                 for i in range(len(parts), 0, -1):
#                                     substring = " ".join(parts[:i]).title().strip()
#                                     debug_log(f"🔁 Retrying click with fallback: text='{substring}'")
#                                     try:
#                                         await page.click(f"text='{substring}'")
#                                         debug_log(f"💼 Fallback click used: text='{substring}'")
#                                         break
#                                     except Exception:
#                                         continue
#                             else:
#                                 debug_log(f"❌ Click failed and no fallback available")
#                                 raise
#                     # <<end 03-JUN-2025:20:55>>

#                 elif action == "click_by_role":
#                     # <<02-JUN-2025:22:45>> – Use toggle_checkbox_under_section from this module
#                     if step.get("role") == "checkbox":
#                         label = step.get("name")
#                         section = step.get("context")  # e.g., "Invoices on Hold"
#                         debug_log(f"🖱️ Checking checkbox '{label}' under section '{section}'")
#                         await toggle_checkbox_under_section(page, label=label, section=section, check=True)
#                     else:
#                         debug_log(f"🖱️ Clicking by role: {step['role']} name: {step['name']}")
#                         await page.get_by_role(step["role"], name=step["name"]).click()
#                     # <<end 02-JUN-2025:22:45>>

#                 elif action == "evaluate_click":
#                     debug_log(f"🖱️ Evaluating click on: {selector}")
#                     await page.evaluate(f"document.querySelector('{selector}').click()")

#                 elif action == "wait_for_selector":
#                     # <<04-JUN-2025:07:30>> – For 'Export', attempt role-based wait first before CSS
#                     if selector and selector.startswith("css=") and "export" in selector:
#                         debug_log("🔍 Trying role-based wait for 'Export to Excel' button first")
#                         try:
#                             await page.get_by_role("button", name="Export to Excel").first.wait_for(state="visible", timeout=step.get("timeout", 30000))
#                             debug_log("💼 Role-based wait succeeded for 'Export to Excel'")
#                             raise Exception("Skip CSS wait for export")
#                         except Exception as e_btn:
#                             if str(e_btn) == "Skip CSS wait for export":
#                                 raise
#                             debug_log(f"⚠️ Role-based export wait failed: {e_btn}, falling back to CSS")
#                     # <<end 04-JUN-2025:07:30>>

#                     # <<03-JUN-2025:20:55>> – Enhanced wait logic for raw CSS selectors with fallback
#                     debug_log(f"🔍 Waiting for selector: {selector} timeout {step.get('timeout', 30000)}")
#                     timeout = step.get("timeout", 30000)
#                     if selector and selector.startswith("css="):
#                         raw_css = selector.split("=", 1)[1]
#                         escaped_css = ensure_escaped_selector(raw_css)
#                         try:
#                             debug_log(f"🔁 Waiting for escaped CSS: css={escaped_css}")
#                             await page.wait_for_selector(f"css={escaped_css}", timeout=timeout)
#                         except Exception as css_wait_error:
#                             debug_log(f"⚠️ CSS wait failed: {css_wait_error}")
#                             if "export" in raw_css:
#                                 debug_log("🔁 Fallback waiting for 'Export to Excel' button")
#                                 await page.get_by_role("button", name="Export to Excel").first.wait_for(state="visible", timeout=timeout)
#                             else:
#                                 label = raw_css.split(".")[-1].replace("-", " ").title()
#                                 section = step.get("context")
#                                 if section:
#                                     debug_log(f"🔁 Fallback waiting for checkbox '{label}' under section '{section}'")
#                                     checkbox = page.get_by_role("row", name=section).get_by_role("checkbox", name=label)
#                                 else:
#                                     debug_log(f"🔁 Fallback waiting for first checkbox named '{label}' (no context provided)")
#                                     checkbox = page.get_by_role("checkbox", name=label).first
#                                 await checkbox.wait_for(state="visible", timeout=timeout)
#                     else:
#                         # Original wait logic
#                         await page.wait_for_selector(selector, timeout=step.get("timeout", 30000))
#                     # <<end 03-JUN-2025:20:55>>

#                 elif action == "wait_for_timeout":
#                     debug_log(f"⏳ Waiting for timeout: {value} ms")
#                     await page.wait_for_timeout(int(value))

#                 elif action == "assert":
#                     debug_log(f"🔍 Asserting '{value}' in page content")
#                     content = await page.content()
#                     if value not in content:
#                         raise Exception(f"Assertion failed: '{value}' not found")

#                 elif action == "debug_pause":
#                     await page.pause()
#                     continue

#                 # <<03-JUN-2025:11:45>> – (Deprecated) inline 'click_select_all' remains commented out
#                 # <<end 03-JUN-2025:11:45>>

#                 debug_log(f"✅ Step succeeded: {action} - {selector}")
#                 filename = f"{timestamp}_sess_{session_id}_step_{step_num}_{action}"
#                 await capture_screenshot(page, session_id, filename, step_num)
#                 html_content = await page.content()
#                 await log_html_to_file(step_num, html_content, session_id)

#             except Exception as e:
#                 # Handle controlled skips for select-all and export
#                 if str(e) in (
#                     "Skip CSS click for select-all",
#                     "Skip CSS click for export",
#                     "Skip CSS wait for export"
#                 ):
#                     debug_log(f"🔁 Skipped CSS block because action succeeded via role-based method: {e}")
#                     filename = f"{timestamp}_sess_{session_id}_step_{step_num}_{action}"
#                     await capture_screenshot(page, session_id, filename, step_num)
#                     html_content = await page.content()
#                     await log_html_to_file(step_num, html_content, session_id)
#                     continue

#                 debug_log(f"❌ Step failed: {action} - {selector} - {e}")
#                 error_filename = f"{timestamp}_sess_{session_id}_step_{step_num}_{action}_error"
#                 await capture_screenshot(page, session_id, error_filename, step_num)
#                 html_content = await page.content()
#                 await log_html_to_file(f"{step_num}_error", html_content, session_id)

#         # After all steps, retrieve final page HTML
#         html = await page.content()
#         # COMMENTED OUT to keep browser open for debugging
#         # await context.close()
#         # <<31-MAY-2025:18:30>> – Commented out old close+return so crawler can reuse page/browser
#         # await browser.close()
#         # debug_log("Exited run_browser_script")
#         # return html

#         # <<31-MAY-2025:18:30>> – Now return (page, browser, already_logged_in) so caller can continue
#         return page, browser, already_logged_in

#     except Exception as e:
#         debug_log(f"❌ Playwright error: {e}")
#         # <<31-MAY-2025:18:30>> – On exception, return a consistent tuple
#         return None, None, False


# # <<02-JUN-2025:22:45>> – Added helper for checkbox toggling within this module
# async def toggle_checkbox_under_section(page, label: str, section: str, check: bool = True):
#     """
#     Toggles a checkbox by its ARIA name under a given table/row context.
#     Parameters:
#       - page: Playwright Page object
#       - label: The visible checkbox label (e.g., "Select All" or invoice number)
#       - section: The parent row or table name (e.g., "Invoices on Hold")
#       - check: True to check, False to uncheck
#     """
#     debug_log(f"Entered: toggle_checkbox_under_section(label='{label}', section='{section}', check={check})")
#     # Scope under the row named "section"
#     row_locator = page.get_by_role("row", name=section)
#     checkbox = row_locator.get_by_role("checkbox", name=label)
#     if check:
#         await checkbox.check()
#     else:
#         await checkbox.uncheck()
#     debug_log(f"Exited: toggle_checkbox_under_section(label='{label}', section='{section}', check={check})")


# # <<31-MAY-2025:18:30>> – Added helper to return only HTML when needed
# async def run_browser_script_html(
#     *,
#     steps: list[dict],
#     session_id: str,
#     login_url: str,
#     username: str,
#     password: str,
#     preview_mode: bool = False,
# ):
#     """
#     <<31-MAY-2025:18:30>> – Convenience wrapper for callers who only want HTML.
#     """
#     page, browser, already_logged_in = await run_browser_script(
#         steps=steps,
#         session_id=session_id,
#         login_url=login_url,
#         username=username,
#         password=password,
#         preview_mode=preview_mode,
#     )
#     if page:
#         html = await page.content()
#         # <<31-MAY-2025:18:30>> – Close browser here since caller only wants HTML
#         await browser.close()
#         return html
#     return ""


# async def run_single_selector_step(selector, login_url, username, password, session_id="executor_test"):
#     debug_log("🎯 Running single selector through run_browser_script")
#     steps = [{
#         "action": "click",
#         "selector": selector
#     }]
#     return await run_browser_script(
#         steps=steps,
#         login_url=login_url,
#         username=username,
#         password=password,
#         session_id=session_id,
#         preview_mode=False
#     )
# 

# <<31-MAY-2025:16:28>> - Merged cookie-based persistence and DOM extraction into existing path_crawler version
from playwright.async_api import async_playwright
from utils.logging import debug_log, capture_screenshot, log_html_to_file
from utils.selectors import ensure_escaped_selector
from datetime import datetime
from oracle.login_steps import run_oracle_login_steps
from oracle.locators import LOCATORS
from oracle.navigation import load_ui_map, find_page_id_by_label, navigate_to as async_navigate_to
from services.browser_service import browser_service
from dotenv import load_dotenv
import os
import re


async def run_browser_script(
    *,
    steps: list[dict],
    session_id: str,
    login_url: str,
    username: str,
    password: str,
    preview_mode: bool = False,
    target_label: str = None,
    parent_label: str = None,
    page=None,
    browser=None,
    already_logged_in: bool = False
):
    """
    Execute a series of Playwright steps with robust handling:
    - Auto-login for Oracle Cloud
    - Generic nav-link mapping
    - Select All and Export logic
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    debug_log("Entered run_browser_script")
    debug_log(f"Preview Mode: {preview_mode}")
    debug_log(f"Steps to execute: {len(steps)}")
    debug_log(f"Target label: {target_label}")
    debug_log(f"Parent label: {parent_label}")

    # Preview mode shortcut
    if preview_mode:
        for idx, step in enumerate(steps, 1):
            debug_log(f"[Preview] Step {idx}: {step}")
        debug_log("Skipping execution due to preview mode")
        debug_log("Exited run_browser_script")
        return "Preview mode — no browser actions executed."

    try:
        # Load environment and determine headless
        load_dotenv()
        headless_mode = os.getenv("HEADLESS", "true").lower() == "true"

        # Launch or reuse context
        if page is None or browser is None:
            debug_log("No existing page/browser – launching new Playwright context")
            p = await async_playwright().start()
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            # Fresh login
            if not already_logged_in:
                debug_log("Performing login on fresh context")
                await run_oracle_login_steps(
                    page, login_url, username, password, session_id, page.url
                )
                already_logged_in = True
                debug_log(f"Login success – landed on: {page.url}")

                # Mapped navigation if requested
                if target_label:
                    debug_log(
                        f"Starting mapped navigation for: {parent_label} → {target_label}"
                    )
                    ui_map = load_ui_map("oracle/ui_map.jsonl")
                    page_id = find_page_id_by_label(
                        ui_map, target_label, parent_label
                    )
                    if page_id:
                        debug_log(f"Resolved target page ID: {page_id}, executing navigation")
                        await async_navigate_to(
                            page, "oracle/ui_map.jsonl", page_id
                        )
                    else:
                        debug_log(
                            f"Unable to resolve navigation to {target_label} under {parent_label}"
                        )
        else:
            debug_log("Reusing existing page/browser context")
            if not already_logged_in:
                debug_log("Performing login on existing context")
                await run_oracle_login_steps(
                    page, login_url, username, password, session_id, page.url
                )
                already_logged_in = True
                debug_log(f"Login success – landed on: {page.url}")

        # Process each step
        for step_num, step in enumerate(steps, 1):
            action   = step.get("action")
            selector = step.get("selector")
            value    = step.get("value")
            context  = step.get("context")
            rowName  = step.get("rowName")
            debug_log(
                f"Step {step_num}: {action} - selector: {selector} - value: {value}"
                f" - context: {context} - rowName: {rowName}"
            )

            # --- Generic nav-link.text-dark mapping ---
            if selector:
                norm_sel = selector[4:] if selector.startswith("css=") else selector
                if norm_sel.startswith(".nav-link.text-dark."):
                    slug = norm_sel.split(".")[-1]
                    label = slug.replace("-", " ").title()
                    debug_log(
                        f"Generic nav-link mapping: turning '{selector}' into text='{label}'"
                    )
                    selector = f"text='{label}'"

            # Suppress 'Show More'
            if action == "click" and selector and "show-more" in selector:
                debug_log("Skipping 'Show More' click")
                continue

            try:
                # Navigate
                if action == "goto":
                    debug_log(f"GOTO Navigating to: {value}")
                    await page.goto(value)

                # Fill input
                elif action == "fill":
                    debug_log(f"Filling '{selector}' with '{value}'")
                    await page.fill(selector, value)

                # Click using locator regex (Select All)
                elif action == "click_locator":
                    debug_log("Running select-all via codegen pattern (div.filter)")
                    await page.locator("div").filter(
                        has_text=re.compile(r"^Select All$")
                    ).first.click()
                    html = await page.content()
                    await log_html_to_file(step_num, html, session_id)
                    continue

                # Role-based check (Select All)
                elif action == "check_by_role":
                    label   = step.get("name")
                    section = rowName or ""
                    debug_log(
                        f"Running check_by_role under section '{section}' for '{label}'"
                    )
                    if section:
                        await page.get_by_role("row", name=section).get_by_label(label).check()
                    else:
                        await page.get_by_label(label).first.check()
                    html = await page.content()
                    await log_html_to_file(step_num, html, session_id)
                    continue

                # Export to Excel with download capture
                elif (
                    action == "click_by_role"
                    and step.get("role") == "button"
                    and step.get("name") == "Export to Excel"
                ) or (
                    action == "click"
                    and selector
                    and "export" in selector.lower()
                ):
                    debug_log("Running export via async expect_download()")
                    async with page.expect_download() as download_info:
                        await page.get_by_role("button", name="Export to Excel").first.click()
                    download = download_info.value
                    debug_log(f"Download started: {await download.path()}")
                    html = await page.content()
                    await log_html_to_file(step_num, html, session_id)
                    continue

                # Simple click fallback
                elif action == "click":
                    await page.click(selector)

                # Evaluate JS click
                elif action == "evaluate_click":
                    debug_log(f"Evaluating click on: {selector}")
                    await page.evaluate(
                        f"document.querySelector('{selector}').click()"
                    )

                # Wait for selector, text or CSS
                elif action == "wait_for_selector":
                    debug_log(f"Waiting for selector: {selector}")
                    timeout = step.get("timeout", 30000)
                    if selector.startswith("text=") or ".nav-link.text-dark." in selector:
                        debug_log(f"Locator.wait_for for: {selector}")
                        await page.locator(selector).wait_for(
                            state="visible", timeout=timeout
                        )
                    else:
                        await page.wait_for_selector(selector, timeout=timeout)
                    continue

                # ...additional actions like wait_for_timeout, assert, debug_pause
                elif action == "wait_for_timeout":
                    await page.wait_for_timeout(int(value))

                elif action == "assert":
                    content = await page.content()
                    if value not in content:
                        raise Exception(f"Assertion failed: '{value}' not found")

                elif action == "debug_pause":
                    await page.pause()
                    continue

                # Success logging
                debug_log(f"✅ Step succeeded: {action}")
                await capture_screenshot(
                    page, session_id, f"{timestamp}_step_{step_num}_{action}", step_num
                )
                html = await page.content()
                await log_html_to_file(step_num, html, session_id)

            except Exception as e:
                debug_log(f"❌ Step failed: {action} - {e}")
                await capture_screenshot(
                    page, session_id, f"{timestamp}_error_{step_num}", step_num
                )
                html = await page.content()
                await log_html_to_file(f"{step_num}_error", html, session_id)

        # Return the running context
        return page, browser, already_logged_in

    except Exception as err:
        debug_log(f"❌ Playwright error: {err}")
        return None, None, False


async def toggle_checkbox_under_section(
    page,
    label: str,
    section: str,
    check: bool = True
):
    debug_log(
        f"Entered toggle_checkbox_under_section(label='{label}', section='{section}', check={check})"
    )
    row_locator = page.get_by_role("row", name=section)
    checkbox    = row_locator.get_by_role("checkbox", name=label)
    if check:
        await checkbox.check()
    else:
        await checkbox.uncheck()
    debug_log(
        f"Exited toggle_checkbox_under_section(label='{label}', section='{section}', check={check})"
    )


async def run_browser_script_html(
    *,
    steps: list[dict],
    session_id: str,
    login_url: str,
    username: str,
    password: str,
    preview_mode: bool = False
):
    page, browser, logged_in = await run_browser_script(
        steps=steps,
        session_id=session_id,
        login_url=login_url,
        username=username,
        password=password,
        preview_mode=preview_mode,
    )
    if page:
        html = await page.content()
        await browser.close()
        return html
    return ""


async def run_single_selector_step(
    selector,
    login_url,
    username,
    password,
    session_id: str = "executor_test"
):
    debug_log("Running single selector through run_browser_script")
    steps = [{"action": "click", "selector": selector}]
    return await run_browser_script(
        steps=steps,
        login_url=login_url,
        username=username,
        password=password,
        session_id=session_id,
        preview_mode=False,
    )
