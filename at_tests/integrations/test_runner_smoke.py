# at_tests/integrations/test_runner_smoke.py
# <<08-JUN-2025:00:38>> - Minimal Playwright runner smoke-test

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True), override=False)          # pick up .env

import os
import pytest
from playwright.async_api import async_playwright

# import path: services.playwright_runner_core
from services.playwright_runner_core import run_browser_script

# --------------------------------------------------------------------------- #
#  Env-driven login values (defaults keep test offline)
# --------------------------------------------------------------------------- #
LOGIN_URL = os.getenv("ORACLE_LOGIN_URL", "https://example.com/login")
USERNAME  = os.getenv("ORACLE_USERNAME",  "dummy")
PASSWORD  = os.getenv("ORACLE_PASSWORD",  "dummy")

# Simple no-op step list – change as needed
SMOKE_STEPS = [
    {"action": "goto",             "value": "https://example.com"},
    {"action": "wait_for_timeout", "value": "1000"},
]

# --------------------------------------------------------------------------- #
#  Smoke test
# --------------------------------------------------------------------------- #
@pytest.mark.asyncio
async def test_smoke_runner():
    async with async_playwright():
        page, browser, logged_in = await run_browser_script(
            steps=SMOKE_STEPS,
            session_id="smoke",
            login_url=LOGIN_URL,
            username=USERNAME,
            password=PASSWORD,
            already_logged_in=True,      # skip real Oracle login for smoke
        )

        # Sanity assertions
        assert browser is not None
        assert page is not None
        await browser.close()
