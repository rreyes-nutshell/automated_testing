# from playwright.async_api import async_playwright
# from utils.logging import debug_log, capture_screenshot, log_html_to_file
# from utils.selectors import ensure_escaped_selector
# from datetime import datetime
# from oracle.login_steps import run_oracle_login_steps
# from oracle.locators import LOCATORS
# from oracle.navigation import load_ui_map, find_page_id_by_label, navigate_to as async_navigate_to
# import os
# import re


# async def run_browser_script(steps, session_id=None, login_url=None, username=None, password=None,
#                              preview_mode=False, target_label=None, parent_label=None):
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     debug_log("Entered")
#     debug_log(f"🧙️ Preview Mode: {preview_mode}")

#     debug_log(f"🧩 Steps to execute: {len(steps)}"  )
#     debug_log(f"Target label: {target_label}")
#     debug_log(f"Parent label: {parent_label}")




#     if preview_mode:
#         for step_num, step in enumerate(steps, 1):
#             debug_log(f"🖟️ [Preview] Step {step_num}: {step}")
#         debug_log("🕔️ Skipping execution due to preview mode")
#         debug_log("Exited")
#         return "Preview mode — no browser actions executed."

#     try:
#         headless_mode = os.getenv("HEADLESS", "true").lower() == "true"

#         async with async_playwright() as p:
#             browser = await p.chromium.launch(headless=False)
#             context = await browser.new_context()
#             page = await context.new_page()

#             if not login_url or not username or not password:
#                 debug_log(f"❌ Skipping login — Missing one of login_url ({login_url}), username ({username}), or password.")
#             else:
#                 try:
#                     await run_oracle_login_steps(page, login_url, username, password, session_id, page.url)
#                     debug_log(f"🔍 Login success — landed on: {page.url}")
#                     if target_label:
#                         debug_log(f"🔎 Starting mapped navigation for: {parent_label} → {target_label}")
#                         ui_map = load_ui_map("oracle/ui_map.jsonl")
#                         page_id = find_page_id_by_label(ui_map, target_label, parent_label)
#                         if page_id:
#                             debug_log(f"🔗 Resolved target page ID: {page_id}, executing navigation")
#                             await async_navigate_to(page, "oracle/ui_map.jsonl", page_id)
#                         else:
#                             debug_log(f"⚠️ Unable to resolve navigation to {target_label} under {parent_label}")
#                 except Exception as login_err:
#                     debug_log(f"❌ Login failed: {login_err}")
#                     error_filename = f"{timestamp}_sess_{session_id}_login_error"
#                     await capture_screenshot(page, session_id, error_filename, 0)
#                     html_content = await page.content()
#                     await log_html_to_file("0_login_error", html_content, session_id)
#                     await browser.close()
#                     return ""

#             for step_num, step in enumerate(steps, 1):
#                 action = step.get("action")
#                 selector = step.get("selector")
#                 value = step.get("value")
#                 debug_log(f"🔁 Step {step_num}: {action} - {selector} - {value}"    )
#                 selector = ensure_escaped_selector(selector)
#                 debug_log(f"🔁 Ensured selector: {selector}" )

#                 if selector == ".button[title='Navigator']":
#                     debug_log(f"🔁 Normalizing selector at step {step_num} from .button[title='Navigator'] to a[title='Navigator']")
#                     selector = "a[title='Navigator']"

#                 if selector and ":contains(" in selector:
#                     match = re.search(r":contains\((.*?)\)", selector)
#                     if match:
#                         label = match.group(1).strip("\"'")
#                         debug_log(f"🔁 Rewriting selector '{selector}' to text='{label}'")
#                         selector = f"text='{label}'"

#                 if selector in [LOCATORS.get("User ID"), LOCATORS.get("Password")] and "AtkHomePageWelcome" in page.url:
#                     debug_log(f"⚠️ Skipping step {step_num}: Already logged in, selector {selector} not needed.")
#                     continue

#                 if action == "click" and selector and "show-more" in selector:
#                     debug_log(f"🛑 Skipping step {step_num}: Suppressed 'Show More' click")
#                     continue

#                 try:
#                     if action == "goto":
#                         debug_log(f"🔗 GOTO Navigating to: {value}"  )
#                         await page.goto(value)
#                     elif action == "fill":
#                         debug_log(f"✏️ Filling selector '{selector}' with value '{value}'")
#                         await page.fill(selector, value)
#                     elif action == "click":
#                         try:
#                             debug_log(f"🖱️ Clicking selector '{selector}'")
#                             element = page.locator(selector)
#                             await element.scroll_into_view_if_needed()
#                             await element.hover()
#                             await element.click()
#                             await page.wait_for_timeout(5000)
#                             debug_log(f"💼 Clicked selector '{selector}'")
#                         except Exception as click_error:
#                             debug_log(f"⚠️ Primary click failed for selector '{selector}': {click_error}")
#                             if selector and selector.startswith("#"):
#                                 raw_label = selector.split(" > ")[0].strip("#")
#                                 parts = raw_label.replace("_", "-").split("-")
#                                 for i in range(len(parts), 0, -1):
#                                     substring = " ".join(parts[:i]).title().strip()
#                                     debug_log(f"🔁 Retrying click with fallback text selector: text='{substring}'")
#                                     try:
#                                         await page.click(f"text='{substring}'")
#                                         debug_log(f"💼 Fallback click selector used: text='{substring}'")
#                                         break
#                                     except Exception:
#                                         continue
#                             else:
#                                 raise
#                     elif action == "click_by_role":
#                         await page.get_by_role(step["role"], name=step["name"]).click()
#                     elif action == "evaluate_click":
#                         await page.evaluate(f"document.querySelector('{selector}').click()")
#                     elif action == "wait_for_selector":
#                         await page.wait_for_selector(selector, timeout=step.get("timeout", 30000))
#                     elif action == "wait_for_timeout":
#                         await page.wait_for_timeout(int(value))
#                     elif action == "assert":
#                         content = await page.content()
#                         if value not in content:
#                             raise Exception(f"Assertion failed: '{value}' not found in page")
#                     elif action == "debug_pause":
#                         await page.pause()
#                         continue

#                     debug_log(f"✅ Step succeeded: {action} - {selector}")
#                     filename = f"{timestamp}_sess_{session_id}_step_{step_num}_{action}"
#                     await capture_screenshot(page, session_id, filename, step_num)
#                     html_content = await page.content()
#                     await log_html_to_file(step_num, html_content, session_id)

#                 except Exception as e:
#                     debug_log(f"❌ Step failed: {action} - {selector} - {e}")
#                     error_filename = f"{timestamp}_sess_{session_id}_step_{step_num}_{action}_error"
#                     await capture_screenshot(page, session_id, error_filename, step_num)
#                     html_content = await page.content()
#                     await log_html_to_file(f"{step_num}_error", html_content, session_id)

#             html = await page.content()
#             await context.close()
#             await browser.close()
#             debug_log("Exited")
#             return html

#     except Exception as e:
#         debug_log(f"❌ Playwright error: {e}")
#         return ""

# async def run_single_selector_step(selector, login_url, username, password, session_id="executor_test"):
# 	debug_log("🎯 Running single selector through run_browser_script")
# 	steps = [{
# 		"action": "click",
# 		"selector": selector
# 	}]
# 	return await run_browser_script(
# 		steps=steps,
# 		login_url=login_url,
# 		username=username,
# 		password=password,
# 		session_id=session_id,
# 		preview_mode=False
# 	)
# from playwright.async_api import async_playwright
# from utils.logging import debug_log, capture_screenshot, log_html_to_file
# from utils.selectors import ensure_escaped_selector
# from datetime import datetime
# from oracle.login_steps import run_oracle_login_steps
# from oracle.locators import LOCATORS
# from oracle.navigation import load_ui_map, find_page_id_by_label, navigate_to as async_navigate_to
# from services.browser_service import browser_service
# import os
# import re


# async def run_browser_script(steps, session_id=None, login_url=None, username=None, password=None,
#                              preview_mode=False, target_label=None, parent_label=None):
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     debug_log("Entered")
#     debug_log(f"🧙️ Preview Mode: {preview_mode}")
#     debug_log(f"🧩 Steps to execute: {len(steps)}")
#     debug_log(f"Target label: {target_label}")
#     debug_log(f"Parent label: {parent_label}")

#     if preview_mode:
#         for idx, step in enumerate(steps, 1):
#             debug_log(f"🖟️ [Preview] Step {idx}: {step}")
#         debug_log("🕔️ Skipping execution due to preview mode")
#         debug_log("Exited")
#         return "Preview mode — no browser actions executed."

#     try:
#         headless_mode = os.getenv("HEADLESS", "true").lower() == "true"

#         # OLD CODE: launch a fresh Playwright context on each run
#         # async with async_playwright() as p:
#         #     browser = await p.chromium.launch(headless=False)
#         #     context = await browser.new_context()
#         #     page = await context.new_page()
#         # NEW CODE: reuse the shared persistent context
#         context = await browser_service.get_context()
#         # Diagnostics: inspect existing cookies
#         cookies = await context.cookies()
#         oracle_cookies = [c for c in cookies if "oraclecloud.com" in c.get("domain", "")]
#         debug_log(f"🔑 Loaded Oracle cookies: {oracle_cookies}")

#         page = context.pages[0] if context.pages else await context.new_page()
#         # Bring the browser window to front
#         try:
#             await page.bring_to_front()
#         except Exception as e:
#             debug_log(f"⚠️ bring_to_front failed: {e}")

#         # Perform login if credentials provided
#         if not login_url or not username or not password:
#             debug_log(f"❌ Skipping login — Missing login_url, username, or password.")
#         else:
#             try:
#                 await run_oracle_login_steps(page, login_url, username, password, session_id, page.url)
#                 debug_log(f"🔍 Login success — landed on: {page.url}")
#                 if target_label:
#                         debug_log(f"🔎 Starting mapped navigation for: {parent_label} → {target_label}")
#                         ui_map = load_ui_map("oracle/ui_map.jsonl")
#                         page_id = find_page_id_by_label(ui_map, target_label, parent_label)
#                         if page_id:
#                             debug_log(f"🔗 Resolved target page ID: {page_id}, executing navigation")
#                             await async_navigate_to(page, "oracle/ui_map.jsonl", page_id)
#                         else:
#                             debug_log(f"⚠️ Unable to resolve navigation to {target_label} under {parent_label}")
#             except Exception as login_err:
#                     debug_log(f"❌ Login failed: {login_err}")
#                     error_filename = f"{timestamp}_sess_{session_id}_login_error"
#                     await capture_screenshot(page, session_id, error_filename, 0)
#                     html_content = await page.content()
#                     await log_html_to_file("0_login_error", html_content, session_id)
#             # COMMENTED OUT to keep browser open for debugging
#             # await browser.close()
#                     return ""

#             for step_num, step in enumerate(steps, 1):
#                 action = step.get("action")
#                 selector = step.get("selector")
#                 value = step.get("value")
#                 debug_log(f"🔁 Step {step_num}: {action} - {selector} - {value}"    )
#                 selector = ensure_escaped_selector(selector)
#                 debug_log(f"🔁 Ensured selector: {selector}")

#                 # Simplify LLM-derived selectors to base id selector (keep full ID with colons)
#                 if '\.' in selector:
#                     base_sel = selector.split('\.')[0]
#                 elif '.' in selector:
#                     base_sel = selector.split('.')[0]
#                 else:
#                     base_sel = selector
#                 # Unescape the hash so it's a literal '#'
#                 base_sel = base_sel.replace('\#', '#')
#                 if base_sel != selector:
#                     debug_log(f"🔄 Simplifying selector from LLM '{selector}' to '{base_sel}'")
#                     selector = base_sel


#                 if selector == ".button[title='Navigator']":
#                     debug_log(f"🔁 Normalizing selector at step {step_num} from .button[title='Navigator'] to a[title='Navigator']")
#                     selector = "a[title='Navigator']"

#                 if selector and ":contains(" in selector:
#                     match = re.search(r":contains\((.*?)\)", selector)
#                     if match:
#                         label = match.group(1).strip("\"'")
#                         debug_log(f"🔁 Rewriting selector '{selector}' to text='{label}'")
#                         selector = f"text='{label}'"

#                 if selector in [LOCATORS.get("User ID"), LOCATORS.get("Password")] and "AtkHomePageWelcome" in page.url:
#                     debug_log(f"⚠️ Skipping step {step_num}: Already logged in, selector {selector} not needed.")
#                     continue

#                 if action == "click" and selector and "show-more" in selector:
#                     debug_log(f"🛑 Skipping step {step_num}: Suppressed 'Show More' click")
#                     continue

#                 try:
#                     if action == "goto":
#                         debug_log(f"🔗 GOTO Navigating to: {value}"  )
#                         await page.goto(value)
#                     elif action == "fill":
#                         debug_log(f"✏️ Filling selector '{selector}' with value '{value}'")
#                         await page.fill(selector, value)
#                     elif action == "click":
#                         try:
#                             debug_log(f"🖱️ Clicking selector '{selector}'")
#                             debug_log(f"🖱️ Clicking selector '{selector}'")
#                             debug_log(f"🖱️ Clicking selector '{selector}'")
#                             debug_log(f"🖱️ Clicking selector '{selector}'")
#                             element = page.locator(selector)
#                             await element.scroll_into_view_if_needed()
#                             await element.hover()
#                             await element.click()
#                             await page.wait_for_timeout(5000)
#                             debug_log(f"💼 Clicked selector '{selector}'")
#                         except Exception as click_error:
#                             debug_log(f"⚠️ Primary click failed for selector '{selector}': {click_error}")
#                             if selector and selector.startswith("#"):
#                                 raw_label = selector.split(" > ")[0].strip("#")
#                                 parts = raw_label.replace("_", "-").split("-")
#                                 for i in range(len(parts), 0, -1):
#                                     substring = " ".join(parts[:i]).title().strip()
#                                     debug_log(f"🔁 Retrying click with fallback text selector: text='{substring}'")
#                                     try:
#                                         await page.click(f"text='{substring}'")
#                                         debug_log(f"💼 Fallback click selector used: text='{substring}'")
#                                         break
#                                     except Exception:
#                                         continue
#                             else:
#                                 debug_log(f"❌ Click failed for selector '{selector}' and no fallback available")
#                                 raise
#                     elif action == "click_by_role":
#                         debug_log(f"🖱️ Clicking by role: {step['role']} with name: {step['name']}")
#                         await page.get_by_role(step["role"], name=step["name"]).click()
#                     elif action == "evaluate_click":
#                         debug_log(f"🖱️ Evaluating click on selector: {selector}")
#                         await page.evaluate(f"document.querySelector('{selector}').click()")
#                     elif action == "wait_for_selector":
#                         debug_log(f"🔍 Waiting for selector: {selector} with timeout {step.get('timeout', 30000)}")
#                         await page.wait_for_selector(selector, timeout=step.get("timeout", 30000))
#                     elif action == "wait_for_timeout":
#                         debug_log(f"⏳ Waiting for timeout: {value} ms")
#                         await page.wait_for_timeout(int(value))
#                     elif action == "assert":
#                         debug_log(f"🔍 Asserting value '{value}' in page content")
#                         content = await page.content()
#                         if value not in content:
#                             raise Exception(f"Assertion failed: '{value}' not found in page")
#                     elif action == "debug_pause":
#                         await page.pause()
#                         continue

#                     debug_log(f"✅ Step succeeded: {action} - {selector}")
#                     filename = f"{timestamp}_sess_{session_id}_step_{step_num}_{action}"
#                     await capture_screenshot(page, session_id, filename, step_num)
#                     html_content = await page.content()
#                     await log_html_to_file(step_num, html_content, session_id)

#                 except Exception as e:
#                     debug_log(f"❌ Step failed: {action} - {selector} - {e}")
#                     error_filename = f"{timestamp}_sess_{session_id}_step_{step_num}_{action}_error"
#                     await capture_screenshot(page, session_id, error_filename, step_num)
#                     html_content = await page.content()
#                     await log_html_to_file(f"{step_num}_error", html_content, session_id)

#             html = await page.content()
#             # COMMENTED OUT to keep browser open for debugging
#             # await context.close()
#             await browser.close()
#             debug_log("Exited")
#             return html

#     except Exception as e:
#         debug_log(f"❌ Playwright error: {e}")
#         return ""

# async def run_single_selector_step(selector, login_url, username, password, session_id="executor_test"):
# 	debug_log("🎯 Running single selector through run_browser_script")
# 	steps = [{
# 		"action": "click",
# 		"selector": selector
# 	}]
# 	return await run_browser_script(
# 		steps=steps,
# 		login_url=login_url,
# 		username=username,
# 		password=password,
# 		session_id=session_id,
# 		preview_mode=False
# 	)
# <<31-MAY-2025:16:28>> - Merged cookie-based persistence and DOM extraction into existing path_crawler version
# playwright_runner.py

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
    If page/browser is passed in, reuse them (so cookies/session persist).
    Otherwise, create a fresh context, sign in, and run steps.
    Returns final page HTML at the end of script execution.
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    debug_log("Entered run_browser_script")
    debug_log(f"🧙️ Preview Mode: {preview_mode}")
    debug_log(f"🧩 Steps to execute: {len(steps)}")
    debug_log(f"Target label: {target_label}")
    debug_log(f"Parent label: {parent_label}")

    if preview_mode:
        for idx, step in enumerate(steps, 1):
            debug_log(f"🖟️ [Preview] Step {idx}: {step}")
        debug_log("🕔️ Skipping execution due to preview mode")
        debug_log("Exited run_browser_script")
        return "Preview mode — no browser actions executed."

    try:
        load_dotenv()
        headless_mode = os.getenv("HEADLESS", "true").lower() == "true"

        # --- Context reuse or fresh launch ---
        if page is None or browser is None:
            debug_log("❇️ No existing page/browser -- launching new Playwright context")
            p = await async_playwright().start()
            browser = await p.chromium.launch(headless=headless_mode)
            context = await browser.new_context()
            page = await context.new_page()

            # Perform login on fresh context
            if not already_logged_in:
                debug_log("🔐 Performing login on fresh context")
                await run_oracle_login_steps(page, login_url, username, password, session_id, page.url)
                already_logged_in = True
                debug_log(f"🔍 Login success — landed on: {page.url}")
                if target_label:
                    debug_log(f"🔎 Starting mapped navigation for: {parent_label} → {target_label}")
                    ui_map = load_ui_map("oracle/ui_map.jsonl")
                    page_id = find_page_id_by_label(ui_map, target_label, parent_label)
                    if page_id:
                        debug_log(f"🔗 Resolved target page ID: {page_id}, executing navigation")
                        await async_navigate_to(page, "oracle/ui_map.jsonl", page_id)
                    else:
                        debug_log(f"⚠️ Unable to resolve navigation to {target_label} under {parent_label}")
        else:
            debug_log("✅ Reusing existing page/browser context")
            # If not yet logged in in this context, perform login
            if not already_logged_in:
                debug_log("🔐 Performing login on existing context")
                await run_oracle_login_steps(page, login_url, username, password, session_id, page.url)
                already_logged_in = True
                debug_log(f"🔍 Login success — landed on: {page.url}")

        # --- At this point, 'page' is logged in and ready ---
        for step_num, step in enumerate(steps, 1):
            action = step.get("action")
            selector = step.get("selector")
            value = step.get("value")
            debug_log(f"🔁 Step {step_num}: {action} - {selector} - {value}")

            # Ensure selector is properly escaped
            if selector:
                selector = ensure_escaped_selector(selector)
                debug_log(f"🔁 Ensured selector: {selector}")

                # Simplify selectors with dots
                if '\\.' in selector:
                    base_sel = selector.split('\\.')[0]
                elif '.' in selector:
                    base_sel = selector.split('.')[0]
                else:
                    base_sel = selector
                base_sel = base_sel.replace('\\#', '#')
                if base_sel != selector:
                    debug_log(f"🔄 Simplifying selector from LLM '{selector}' to '{base_sel}'")
                    selector = base_sel

                if selector == ".button[title='Navigator']":
                    debug_log(f"🔁 Normalizing selector at step {step_num} to a[title='Navigator']")
                    selector = "a[title='Navigator']"

                if ":contains(" in selector:
                    match = re.search(r":contains\((.*?)\)", selector)
                    if match:
                        label = match.group(1).strip("\"'")
                        debug_log(f"🔁 Rewriting selector '{selector}' to text='{label}'")
                        selector = f"text='{label}'"

                # Skip login fields if already on home page
                if selector in [LOCATORS.get("User ID"), LOCATORS.get("Password")] and "AtkHomePageWelcome" in page.url:
                    debug_log(f"⚠️ Skipping step {step_num}: Already logged in, selector {selector} not needed.")
                    continue

            # Skip unwanted clicks
            if action == "click" and selector and "show-more" in selector:
                debug_log(f"🛑 Skipping step {step_num}: Suppressed 'Show More' click")
                continue

            try:
                if action == "goto":
                    debug_log(f"🔗 GOTO Navigating to: {value}")
                    await page.goto(value)
                elif action == "fill":
                    debug_log(f"✏️ Filling selector '{selector}' with value '{value}'")
                    await page.fill(selector, value)
                elif action == "click":
                    try:
                        debug_log(f"🖱️ Clicking selector '{selector}'")
                        element = page.locator(selector)
                        await element.scroll_into_view_if_needed()
                        await element.hover()
                        await element.click()
                        await page.wait_for_timeout(5000)
                        debug_log(f"💼 Clicked selector '{selector}'")
                    except Exception as click_error:
                        debug_log(f"⚠️ Primary click failed: {click_error}")
                        if selector and selector.startswith("#"):
                            raw_label = selector.split(" > ")[0].strip("#")
                            parts = raw_label.replace("_", "-").split("-")
                            for i in range(len(parts), 0, -1):
                                substring = " ".join(parts[:i]).title().strip()
                                debug_log(f"🔁 Retrying click with fallback: text='{substring}'")
                                try:
                                    await page.click(f"text='{substring}'")
                                    debug_log(f"💼 Fallback click used: text='{substring}'")
                                    break
                                except Exception:
                                    continue
                        else:
                            debug_log(f"❌ Click failed and no fallback available")
                            raise
                elif action == "click_by_role":
                    debug_log(f"🖱️ Clicking by role: {step['role']} name: {step['name']}")
                    await page.get_by_role(step["role"], name=step["name"]).click()
                elif action == "evaluate_click":
                    debug_log(f"🖱️ Evaluating click on: {selector}")
                    await page.evaluate(f"document.querySelector('{selector}').click()")
                elif action == "wait_for_selector":
                    debug_log(f"🔍 Waiting for selector: {selector} timeout {step.get('timeout', 30000)}")
                    await page.wait_for_selector(selector, timeout=step.get("timeout", 30000))
                elif action == "wait_for_timeout":
                    debug_log(f"⏳ Waiting for timeout: {value} ms")
                    await page.wait_for_timeout(int(value))
                elif action == "assert":
                    debug_log(f"🔍 Asserting '{value}' in page content")
                    content = await page.content()
                    if value not in content:
                        raise Exception(f"Assertion failed: '{value}' not found")
                elif action == "debug_pause":
                    await page.pause()
                    continue

                debug_log(f"✅ Step succeeded: {action} - {selector}")
                filename = f"{timestamp}_sess_{session_id}_step_{step_num}_{action}"
                await capture_screenshot(page, session_id, filename, step_num)
                html_content = await page.content()
                await log_html_to_file(step_num, html_content, session_id)

            except Exception as e:
                debug_log(f"❌ Step failed: {action} - {selector} - {e}")
                error_filename = f"{timestamp}_sess_{session_id}_step_{step_num}_{action}_error"
                await capture_screenshot(page, session_id, error_filename, step_num)
                html_content = await page.content()
                await log_html_to_file(f"{step_num}_error", html_content, session_id)

        # After all steps, retrieve final page HTML
        html = await page.content()
        # COMMENTED OUT to keep browser open for debugging
        # await context.close()
        await browser.close()
        debug_log("Exited run_browser_script")
        return html

    except Exception as e:
        debug_log(f"❌ Playwright error: {e}")
        return ""


async def run_single_selector_step(selector, login_url, username, password, session_id="executor_test"):
    debug_log("🎯 Running single selector through run_browser_script")
    steps = [{
        "action": "click",
        "selector": selector
    }]
    return await run_browser_script(
        steps=steps,
        login_url=login_url,
        username=username,
        password=password,
        session_id=session_id,
        preview_mode=False
    )
