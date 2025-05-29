# # oracle/login_steps.py
# from utils.logging import debug_log, capture_screenshot, log_html_to_file
# from oracle.locators import LOCATORS


# login_ran = False

# async def run_oracle_login_steps(page, login_url, username, password, session_id=None, current_url=None):    
#     global login_ran
#     debug_log("Entered")

    
#     if not login_ran:
#         await page.goto(login_url)
#         await page.wait_for_load_state('load')

#         if current_url and "AtkHomePageWelcome" in current_url:
#             debug_log(f"⚠️ Already logged in, skipping login inputs — current_url={current_url}")
#             return

#         try:
#             await page.wait_for_selector(LOCATORS["User ID"], timeout=30000)
#             await page.fill(LOCATORS["User ID"], username)
#             debug_log(f"🔑 Username: {username}")

#             await page.wait_for_selector(LOCATORS["Password"], timeout=30000)
#             await page.fill(LOCATORS["Password"], password)
#             debug_log(f"🔑 Password: {'*' * len(password)}")

#             await page.click(LOCATORS["Sign In Button"])
#             await page.wait_for_load_state('networkidle')
#             debug_log("✅ Login form submitted")

#             await page.wait_for_timeout(2000)

#             # Post-login navigation: Hamburger > Show More
#             await page.click(LOCATORS["Navigator"])
#             debug_log("🍔 Clicked hamburger menu")
#             await page.wait_for_timeout(1000)
#             try:
#                 await page.wait_for_selector("text=Show More", timeout=3000)
#                 await page.click("text=Show More")
#                 debug_log("📂 Clicked Show More")
#             except Exception:
#                 debug_log("⚠️ Show More link not found or already expanded")

#         except Exception as e:
#             debug_log(f"❌ Login step error: {e}")
#             if session_id:
#                 await capture_screenshot(page, session_id, "login_error", 0)
#                 html_content = await page.content()
#                 await log_html_to_file("login_error", html_content, session_id)
#             raise e
#         login_ran = True
#     else:
#         debug_log("🔐 Skipping login; already authenticated")
#     debug_log("Exited")

# # Provide static login steps for script parser or dry-run
# oracle_login_steps = [
#     {"action": "goto", "target": "{login_url}"},
#     {"action": "fill", "selector": "input[name='userid']", "value": "{username}"},
#     {"action": "fill", "selector": "input[name='password']", "value": "{password}"},
#     {"action": "click", "selector": "button[type='submit']"},
#     {"action": "wait_for_selector", "selector": "a[title='Navigator']", "value": "visible"},
# ]

# __all__ = ["run_oracle_login_steps", "oracle_login_steps"]
# from utils.logging import debug_log, capture_screenshot, log_html_to_file
# from oracle.locators import LOCATORS

# async def run_oracle_login_steps(page, login_url, username, password, session_id=None, current_url=None):
#     """
#     Logs into Oracle using Playwright. Skips login if session cookies are already present.
#     """
#     debug_log("Entered run_oracle_login_steps")

#     # Check for existing Oracle cookies to decide whether login is needed
#     cookies = await page.context.cookies()
#     if any("oraclecloud.com" in c.get("domain", "") for c in cookies):
#         debug_log("🔐 Existing Oracle cookies found; skipping login steps")
#         # Persist storage state and close context to flush cookies
#         from pathlib import Path, os
#         state_path = Path(os.getenv("PLAYWRIGHT_USER_DATA_DIR", str(Path.home() / ".myapp_playwright_data"))) / "storage_state.json"
#         await page.context.storage_state(path=str(state_path))
#         debug_log(f"🔖 Storage state written to {state_path}")
#         await page.context.close()
#         debug_log("🚪 Closed context to flush persistent data")
#         debug_log("Exited run_oracle_login_steps")
#         return

#     # Navigate to login URL
#     debug_log(f"🔗 Navigating to login_url: {login_url}")
#     await page.goto(login_url)
#     await page.wait_for_selector(LOCATORS["User ID"], timeout=30000)

#     try:
#         # Fill in credentials
#         await page.fill(LOCATORS["User ID"], username)
#         debug_log(f"🔑 Username: {username}")

#         await page.fill(LOCATORS["Password"], password)
#         debug_log(f"🔑 Password: {'*' * len(password)}")

#         # Submit the form
#         await page.click(LOCATORS["Sign In Button"])
#         await page.wait_for_load_state('networkidle')
#         debug_log("✅ Login form submitted")

#         # Post-login navigation: Hamburger > Show More
#         await page.click(LOCATORS["Navigator"])
#         debug_log("🍔 Clicked hamburger menu")
#         await page.wait_for_timeout(1000)
#         try:
#             await page.wait_for_selector("text=Show More", timeout=3000)
#             await page.click("text=Show More")
#             debug_log("📂 Clicked Show More")
#         except Exception:
#             debug_log("⚠️ Show More link not found or already expanded")

#     except Exception as e:
#         debug_log(f"❌ Login step error: {e}")
#         if session_id:
#             await capture_screenshot(page, session_id, "login_error", 0)
#             html_content = await page.content()
#             await log_html_to_file("login_error", html_content, session_id)
#         raise

#     debug_log("Exited run_oracle_login_steps")

# # Provide static login steps for script parser or dry-run
# oracle_login_steps = [
#     {"action": "goto", "target": "{login_url}"},
#     {"action": "fill", "selector": "input[name='userid']", "value": "{username}"},
#     {"action": "fill", "selector": "input[name='password']", "value": "{password}"},
#     {"action": "click", "selector": "button[type='submit']"},
#     {"action": "wait_for_selector", "selector": "a[title='Navigator']", "value": "visible"},
# ]

# __all__ = ["run_oracle_login_steps", "oracle_login_steps"]
from utils.logging import debug_log, capture_screenshot, log_html_to_file
from oracle.locators import LOCATORS

async def run_oracle_login_steps(page, login_url, username, password, session_id=None, current_url=None):
    """
    Logs into Oracle using Playwright. Skips login if session cookies are already present.
    """
    debug_log("Entered run_oracle_login_steps")

    # Check for existing Oracle cookies to decide whether login is needed
    cookies = await page.context.cookies()
    if any("oraclecloud.com" in c.get("domain", "") for c in cookies):
        debug_log("🔐 Existing Oracle cookies found; skipping login steps")
        # NOTE: Commented out persistence flush and context close to keep browser visible
        # from pathlib import Path, os
        # state_path = Path(os.getenv("PLAYWRIGHT_USER_DATA_DIR", str(Path.home() / ".myapp_playwright_data"))) / "storage_state.json"
        # await page.context.storage_state(path=str(state_path))
        # debug_log(f"🔖 Storage state written to {state_path}")
        # await page.context.close()
        # debug_log("🚪 Closed context to flush persistent data")
        debug_log("Exited run_oracle_login_steps")
        return

    # Navigate to login URL
    debug_log(f"🔗 Navigating to login_url: {login_url}")
    await page.goto(login_url)
    await page.wait_for_selector(LOCATORS["User ID"], timeout=30000)

    try:
        # Fill in credentials
        await page.fill(LOCATORS["User ID"], username)
        debug_log(f"🔑 Username: {username}")

        await page.fill(LOCATORS["Password"], password)
        debug_log(f"🔑 Password: {'*' * len(password)}")

        # Submit the form
        await page.click(LOCATORS["Sign In Button"])
        await page.wait_for_load_state('networkidle')
        debug_log("✅ Login form submitted")

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
        raise

    debug_log("Exited run_oracle_login_steps")

# Provide static login steps for script parser or dry-run
oracle_login_steps = [
    {"action": "goto", "target": "{login_url}"},
    {"action": "fill", "selector": "input[name='userid']", "value": "{username}"},
    {"action": "fill", "selector": "input[name='password']", "value": "{password}"},
    {"action": "click", "selector": "button[type='submit']"},
    {"action": "wait_for_selector", "selector": "a[title='Navigator']", "value": "visible"},
]

__all__ = ["run_oracle_login_steps", "oracle_login_steps"]
