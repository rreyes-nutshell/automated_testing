# <<08-JUN-2025:20:28>> - CLI runner for Oracle UI nav extraction with HEADLESS_MODE toggle

import asyncio
from playwright.async_api import async_playwright
from oracle.login_steps import run_oracle_login_steps
from oracle.ui_mapper import extract_nav_metadata
from utils.logging import debug_log, load_env
import os

async def main():
	debug_log("Entered main")
	load_env()

	username = os.getenv("ORA_USER")
	password = os.getenv("ORA_PW")
	login_url = os.getenv("ORA_URL")
	headless_mode = os.getenv("HEADLESS_MODE", "true").lower() == "true"
	debug_log(f"HEADLESS_MODE={headless_mode}")

	if not all([username, password, login_url]):
		debug_log("❌ Missing ORA_USER, ORA_PW, or ORA_URL — aborting.")
		return

	async with async_playwright() as p:
		browser = await p.chromium.launch(headless=headless_mode)
		context = await browser.new_context()
		page = await context.new_page()

		await run_oracle_login_steps(page, login_url, username, password)
		debug_log("🧭 Extracting nav metadata now...")

		# <<08-JUN-2025:21:45>> - Wait for nav container to appear and scroll it into view
		try:
			await page.wait_for_selector("#pt1\:_UISnvr", timeout=15000)
			nav_container = page.locator("#pt1\:_UISnvr")
			await nav_container.scroll_into_view_if_needed()
		except Exception as e:
			debug_log(f"⚠️ Timeout waiting for nav container: {e}")

		# Count and log nav item links after ensuring nav is visible
		nav_items = page.locator("a[id^='pt1:_UISnvr']")
		nav_count = await nav_items.count()
		debug_log(f"📊 Total nav items found: {nav_count}")
		if nav_count == 0:
			debug_log("⚠️ No nav items found. Check page state or selector.")

		await extract_nav_metadata(page, username=username, is_superuser=True)
		debug_log("✅ Crawl completed")

	debug_log("Exited main")

if __name__ == "__main__":
	print("🔧 Running nav_crawler...", flush=True)
	asyncio.run(main())
