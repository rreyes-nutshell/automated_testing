from playwright.async_api import async_playwright
from utils.logging import debug_log, capture_screenshot, log_html_to_file
from datetime import datetime
from oracle.login_steps import run_oracle_login_steps
from oracle.locators import LOCATORS
from oracle.navigation import load_ui_map, find_page_id_by_label, navigate_to as async_navigate_to
import os
import re


async def run_browser_script(steps, session_id=None, login_url=None, username=None, password=None,
                             preview_mode=False, target_label=None, parent_label=None):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    debug_log("Entered")
    debug_log(f"🧪 Preview Mode: {preview_mode}")

    if preview_mode:
        for step_num, step in enumerate(steps, 1):
            debug_log(f"🗟️ [Preview] Step {step_num}: {step}")
        debug_log("🛕️ Skipping execution due to preview mode")
        debug_log("Exited")
        return "Preview mode — no browser actions executed."

    try:
        headless_mode = os.getenv("HEADLESS_MODE", "true").lower() == "true"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless_mode)
            context = await browser.new_context()
            page = await context.new_page()

            if not login_url or not username or not password:
                debug_log(f"❌ Skipping login — Missing one of login_url ({login_url}), username ({username}), or password.")
            else:
                try:
                    await run_oracle_login_steps(page, login_url, username, password, session_id, page.url)
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
                except Exception as login_err:
                    debug_log(f"❌ Login failed: {login_err}")
                    error_filename = f"{timestamp}_sess_{session_id}_login_error"
                    await capture_screenshot(page, session_id, error_filename, 0)
                    html_content = await page.content()
                    await log_html_to_file("0_login_error", html_content, session_id)
                    await browser.close()
                    return ""

            for step_num, step in enumerate(steps, 1):
                action = step.get("action")
                selector = step.get("selector")
                value = step.get("value")

                if selector == ".button[title='Navigator']":
                    debug_log(f"🔁 Normalizing selector at step {step_num} from .button[title='Navigator'] to a[title='Navigator']")
                    selector = "a[title='Navigator']"

                if selector and ":contains(" in selector:
                    match = re.search(r":contains\\((.*?)\\)", selector)
                    if match:
                        label = match.group(1).strip("\"'")
                        debug_log(f"🔁 Rewriting selector '{selector}' to text='{label}'")
                        selector = f"text='{label}'"

                if selector in [LOCATORS.get("User ID"), LOCATORS.get("Password")] and "AtkHomePageWelcome" in page.url:
                    debug_log(f"⚠️ Skipping step {step_num}: Already logged in, selector {selector} not needed.")
                    continue

                if action == "click" and selector and "show-more" in selector:
                    debug_log(f"🛑 Skipping step {step_num}: Suppressed 'Show More' click")
                    continue

                try:
                    if action == "goto":
                        await page.goto(value)
                    elif action == "fill":
                        await page.fill(selector, value)
                    elif action == "click":
                        try:
                            await page.click(selector)
                        except Exception as click_error:
                            debug_log(f"⚠️ Primary click failed for selector '{selector}': {click_error}")
                            if selector and selector.startswith("#"):
                                raw_label = selector.split(" > ")[0].strip("#")
                                parts = raw_label.replace("_", "-").split("-")
                                for i in range(len(parts), 0, -1):
                                    substring = " ".join(parts[:i]).title().strip()
                                    debug_log(f"🔁 Retrying click with fallback text selector: text='{substring}'")
                                    try:
                                        await page.click(f"text='{substring}'")
                                        debug_log(f"📛 Fallback click selector used: text='{substring}'")
                                        break
                                    except Exception:
                                        continue
                            else:
                                raise
                    elif action == "click_by_role":
                        await page.get_by_role(step["role"], name=step["name"]).click()
                    elif action == "evaluate_click":
                        await page.evaluate(f"document.querySelector('{selector}').click()")
                    elif action == "wait_for_selector":
                        await page.wait_for_selector(selector, timeout=step.get("timeout", 30000))
                    elif action == "wait_for_timeout":
                        await page.wait_for_timeout(int(value))
                    elif action == "assert":
                        content = await page.content()
                        if value not in content:
                            raise Exception(f"Assertion failed: '{value}' not found in page")
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

            html = await page.content()
            await context.close()
            await browser.close()
            debug_log("Exited")
            return html

    except Exception as e:
        debug_log(f"❌ Playwright error: {e}")
        return ""
