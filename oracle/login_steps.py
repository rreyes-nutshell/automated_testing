# oracle/login_steps.py
from utils.logging import debug_log, capture_screenshot, log_html_to_file
from oracle.locators import LOCATORS


async def run_oracle_login_steps(page, login_url, username, password, session_id=None, current_url=None):
    debug_log("Entered")

    await page.goto(login_url)
    await page.wait_for_load_state('load')

    if current_url and "AtkHomePageWelcome" in current_url:
        debug_log(f"⚠️ Already logged in, skipping login inputs — current_url={current_url}")
        return

    try:
        await page.wait_for_selector(LOCATORS["User ID"], timeout=30000)
        await page.fill(LOCATORS["User ID"], username)
        debug_log(f"🔑 Username: {username}")

        await page.wait_for_selector(LOCATORS["Password"], timeout=30000)
        await page.fill(LOCATORS["Password"], password)
        debug_log(f"🔑 Password: {'*' * len(password)}")

        await page.click(LOCATORS["Sign In Button"])
        await page.wait_for_load_state('networkidle')
        debug_log("✅ Login form submitted")

        await page.wait_for_timeout(2000)

        # Post-login navigation: Hamburger > Show More
        await page.click(LOCATORS["Navigator"])
        debug_log("🍔 Clicked hamburger menu")
        await page.wait_for_timeout(1000)
        try:
            await page.wait_for_selector("text=Show More", timeout=3000)
            await page.click("text=Show More")
            debug_log("📂 Clicked Show More")
        except Exception:
            debug_log("⚠️ Show More link not found or already expanded")

    except Exception as e:
        debug_log(f"❌ Login step error: {e}")
        if session_id:
            await capture_screenshot(page, session_id, "login_error", 0)
            html_content = await page.content()
            await log_html_to_file("login_error", html_content, session_id)
        raise e

    debug_log("Exited")

# Provide static login steps for script parser or dry-run
oracle_login_steps = [
    {"action": "goto", "target": "{login_url}"},
    {"action": "fill", "selector": "input[name='userid']", "value": "{username}"},
    {"action": "fill", "selector": "input[name='password']", "value": "{password}"},
    {"action": "click", "selector": "button[type='submit']"},
    {"action": "wait_for_selector", "selector": "a[title='Navigator']", "value": "visible"},
]

__all__ = ["run_oracle_login_steps", "oracle_login_steps"]
