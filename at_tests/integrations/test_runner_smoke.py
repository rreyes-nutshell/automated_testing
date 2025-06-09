# <<08-JUN-2025:03:15>> - Updated to use ORA_URL and real selector-based login smoke

import os
import pytest
from playwright.async_api import async_playwright
from utils.logging import debug_log, load_env
from services.playwright_runner_core import run_browser_script

# --------------------------------------------------------------------------- #
#  Smoke Test Steps — now using selector map aware value
# --------------------------------------------------------------------------- #
load_env()
LOGIN_URL = os.getenv("ORA_URL", "https://example.com")
USERNAME  = os.getenv("ORA_USER",  "dummy")
PASSWORD  = os.getenv("ORA_PW",    "dummy")

SMOKE_STEPS = [
	{"action": "goto",             "value": "{login_url}"},
	{"action": "wait_for_timeout", "value": "2000"},
	{"action": "fill",             "selector": "username_input", "value": USERNAME},
	{"action": "fill",             "selector": "password_input", "value": PASSWORD},
	{"action": "click",            "selector": "sign_in_button"},
	{"action": "wait_for_selector","selector": "hamburger_icon"},
]

# --------------------------------------------------------------------------- #
#  Smoke Test
# --------------------------------------------------------------------------- #
@pytest.mark.asyncio
async def test_smoke_runner():
	load_env()
	async with async_playwright():
		debug_log(f"Using login URL: {LOGIN_URL}")
		page, browser, logged_in = await run_browser_script(
			steps=SMOKE_STEPS,
			session_id="smoke",
			login_url=LOGIN_URL,
			username=USERNAME,
			password=PASSWORD,
			preview_mode=False,
		)

		assert logged_in is True
		assert page is not None
		await browser.close()
