# <<10-JUN-2025:22:48>> - Cleaned up session insert logic to prevent duplicate session error and preserved full truncate flow

import asyncio
import argparse
import os
from playwright.async_api import async_playwright
from oracle.login_steps import run_oracle_login_steps
from oracle.ui_mapper.extractor import extract_nav_metadata
from utils.logging import debug_log 
from utils.env import load_env
from utils.db_utils import get_db_connection
from oracle.ui_mapper.db_inserter import insert_crawl_session

async def main():
	debug_log("Entered main")
	load_env()

	parser = argparse.ArgumentParser(description="Oracle Nav Crawler")
	parser.add_argument("--crawler-name", type=str, required=True, help="Session name for crawl")
	args = parser.parse_args()
	crawler_name = args.crawler_name

	TRUNC_TABLES = os.getenv("TRUNC_TABLES", "false").lower() == "true"

	if TRUNC_TABLES:
		debug_log("⚠️ TRUNC_TABLES is enabled — truncating ui_pages and ui_elements")
		conn = get_db_connection()
		cur = conn.cursor()
		cur.execute("""
		TRUNCATE 
			ui_automation.ui_path_items,
			ui_automation.ui_paths,
			ui_automation.ui_elements,
			ui_automation.ui_pages,
			ui_automation.ui_trap_pages,
			ui_automation.ui_crawl_sessions
		RESTART IDENTITY CASCADE;
		""")
		conn.commit()
		cur.close()
		conn.close()

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

		await run_oracle_login_steps(page, login_url, username, password, crawler_name=crawler_name)

		# ✅ Insert session once
		session_id = insert_crawl_session(crawler_name)

		debug_log("🧭 Extracting nav metadata now...")

		# <<12-JUN-2025:12:39>> - Ensure Oracle base URL is fully reloaded before extracting
		await page.goto(login_url)
		await page.wait_for_load_state("networkidle")
		# <<12-JUN-2025:12:44>> - Commented duplicate expand_hamburger_menu call to prevent double toggle
		from oracle.ui_mapper.recursive_crawler import expand_hamburger_menu
		await expand_hamburger_menu(page)
		await page.wait_for_selector("#pt1\:_UISnvr", timeout=20000)
		debug_log("✅ Oracle nav container loaded")
        
		# <<12-JUN-2025:12:41>> - Expand hamburger menu after returning to base URL
		# <<12-JUN-2025:12:44>> - Commented duplicate expand_hamburger_menu call to prevent double toggle
		from oracle.ui_mapper.recursive_crawler import expand_hamburger_menu
		await expand_hamburger_menu(page)

		try:
			await page.wait_for_selector("#pt1\\:_UISnvr", timeout=15000)
			nav_container = page.locator("#pt1\\:_UISnvr")
			await nav_container.scroll_into_view_if_needed()
		except Exception as e:
			debug_log(f"⚠️ Timeout waiting for nav container: {e}")

		nav_items = page.locator("a[id^='pt1:_UISnvr']")
		nav_count = await nav_items.count()
		debug_log(f"📊 Total nav items found: {nav_count}")
		if nav_count == 0:
			debug_log("⚠️ No nav items found. Check page state or selector.")

		try:
			burgers_visited = set()
			await extract_nav_metadata(page=page, session_name=crawler_name, burgers_visited=burgers_visited)

		except Exception as meta_err:
			debug_log(f"❌ extract_nav_metadata crashed: {meta_err}")
		debug_log("✅ Crawl completed")

	debug_log("Exited main")

if __name__ == "__main__":
	print("🔧 Running nav_crawler...", flush=True)
	asyncio.run(main())
