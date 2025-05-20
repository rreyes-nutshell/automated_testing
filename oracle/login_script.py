from utils.logging import debug_log
import os
from datetime import datetime

SCREENSHOT_DIR = os.path.join("instance", "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

async def oracle_login(page, username, password, login_url):
    debug_log("Entered")

    try:
        await page.goto(login_url)
        await page.wait_for_selector('form[name="loginForm"]', timeout=10000)

        await page.fill('input[name="userid"]', username)
        await page.fill('input[name="password"]', password)

        # Log all submit buttons
        buttons = await page.query_selector_all("input[type='submit']")
        for i, b in enumerate(buttons):
            val = await b.get_attribute("value")
            debug_log(f"🔘 Button {i}: {val}")

        # Try normal click, then fallback to force click
        # try:
        # 	await page.wait_for_selector('input[value="Sign In"]', timeout=5000)
        # 	await page.click('input[value="Sign In"]')
        # except Exception as e:
        # 	debug_log(f"⚠️ Standard click failed: {e} — trying force click")
        # 	await page.click('input[value="Sign In"]', force=True)

        # Correct button click for Oracle login
        try:
            await page.wait_for_selector('button#btnActive', timeout=5000)
            await page.click('button#btnActive')
        except Exception as e:
            debug_log(f"⚠️ Standard button click failed: {e} — trying force click")
            await page.click('button#btnActive', force=True)

        await page.wait_for_timeout(3000)

    except Exception as e:
        debug_log(f"❌ Oracle login script error: {e}")
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"oracle_login_{timestamp}.png")
        await page.screenshot(path=screenshot_path)
        debug_log(f"📸 Screenshot saved: {screenshot_path}")

        content = await page.content()
        return f"Login step failed: {e}\n\nPartial page:\n{content[:3000]}"

    debug_log("Exited")
    return await page.content()

