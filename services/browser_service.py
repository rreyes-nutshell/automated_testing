# services/browser_service.py

from dotenv import load_dotenv, find_dotenv
# Load environment variables from .env file
load_dotenv(find_dotenv())

import os
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from utils.logging import debug_log

class BrowserService:
    """
    Provides a single persistent Playwright browser context across your app.
    """
    def __init__(self):
        self._playwright = None
        self._context = None

    async def init(self):
        if self._playwright is None:
            debug_log("🌱 Starting Playwright")
            # Start Playwright
            self._playwright = await async_playwright().start()

            # Determine path for persistent data
            user_data = os.getenv(
                "PLAYWRIGHT_USER_DATA_DIR",
                str(Path.home() / ".myapp_playwright_data")
            )
            Path(user_data).mkdir(parents=True, exist_ok=True)

            # Launch a persistent context so cookies & storage survive restarts
            headless = os.getenv("HEADLESS", "true").lower() == "true"
            self._context = await self._playwright.chromium.launch_persistent_context(
                user_data_dir=user_data,
                headless=headless,
            )

    async def get_context(self):
        """
        Initializes Playwright if needed, returns the persistent BrowserContext.
        """
        await self.init()
        return self._context

    async def get_page(self):
        """
        Returns the first open Page or creates a new one in the persistent context.
        """
        ctx = await self.get_context()
        # Reuse existing page if any
        if ctx.pages:
            return ctx.pages[0]
        # Otherwise open a new tab
        return await ctx.new_page()

# Module-level singleton
browser_service = BrowserService()

# Sync helper for synchronous code (Flask routes, etc.)
def get_page_sync():
    return asyncio.run(browser_service.get_page())
