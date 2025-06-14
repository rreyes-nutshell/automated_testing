# <<13-JUN-2025:20:59>> - Forces icon DOM refresh and visible check before traversal

from utils.logging import debug_log
from utils.selector_resolver import get_selector
from utils.modal_handler import dismiss_modal_if_present
from utils.skip_rules import should_skip_label
from utils.nav_helpers import expand_hamburger_menu  # <<13-JUN-2025:21:12>> - Added to ensure menu is open between crawls
from oracle.ui_mapper.recursive_crawler import crawl_nav_items
from oracle.ui_mapper.db_inserter import insert_ui_path, insert_crawl_session, get_crawl_session_id_by_name
from oracle.login_steps import run_oracle_login_steps
from oracle.ui_mapper.burger_launcher import launch_next_unclicked_icon
import os
from playwright.async_api import Page

# <<13-JUN-2025:22:02>> - Adds index-based resume to avoid burger loop trap

async def extract_nav_metadata(page: Page, session_name: str, burgers_visited=None):
	debug_log("Entered extract_nav_metadata")

	if burgers_visited is None:
		burgers_visited = set()

	visited = {}
	session_id = get_crawl_session_id_by_name(session_name)
	if not session_id:
		session_id = insert_crawl_session(session_name=session_name)

	if not session_id:
		debug_log("❌ Could not create or retrieve crawl session — aborting.")
		debug_log("Exited extract_nav_metadata")
		return

	path_id = insert_ui_path(session_name=session_name, path_name="Top Level Crawl")
	start_index = 0

	try:
		while True:
			label, next_index = await launch_next_unclicked_icon(
				page=page,
				burgers_visited=burgers_visited,
				start_index=start_index
			)

			if not label:
				remaining = "N/A"
				try:
					all_icons = page.locator("a[id^='pt1:_UISnvr']")
					total = await all_icons.count()
					remaining = max(0, total - len(burgers_visited))
				except:
					pass
				debug_log(f"🛑 No more clickable icons. Total visited: {len(burgers_visited)} | Remaining: {remaining}")
				break

			start_index = next_index

			debug_log(f"🧭 Crawling top nav icon: {label}")
			debug_log(f"🍔 burgers_visited so far: {sorted(list(burgers_visited))}")

			try:
				await page.wait_for_load_state("networkidle")
				await page.wait_for_timeout(500)

				await crawl_nav_items(
					page=page,
					path_id=path_id,
					item_label=label,
					visited=visited,
					depth=0,
					session_id=session_id,
					session_name=session_name,
					burgers_visited=burgers_visited
				)

				# ✅ Only mark as visited after actual crawl
				burgers_visited.add(label)
				debug_log(f"✅ Marked {label} as visited after successful crawl")

				debug_log(f"🧼 Finished crawl for {label}, attempting base reset")
				await page.goto(os.getenv("ORA_URL"))
				await page.wait_for_load_state("networkidle")
				await page.wait_for_timeout(1000)

				if "login" in page.url or "signin" in page.url:
					debug_log(f"🔐 Redirected to login — attempting relogin")
					await run_oracle_login_steps(
						page=page,
						login_url=os.getenv("ORA_URL"),
						username=os.getenv("ORA_USER"),
						password=os.getenv("ORA_PASS"),
						session_id=session_id,
						current_url=page.url,
						crawler_name="extractor"
					)
					debug_log("✅ Re-login successful")

			except Exception as e:
				debug_log(f"❌ Failed crawling icon {label}: {e}")

			# Re-open hamburger menu for next icon
			try:
				success = await expand_hamburger_menu(page)
				if success:
					debug_log("📂 Reopened hamburger menu")
				else:
					debug_log("🍔 Hamburger menu already open")
			except Exception as menu_err:
				debug_log(f"⚠️ Failed to re-expand menu: {menu_err}")

	except Exception as outer:
		debug_log(f"❌ extract_nav_metadata error: {outer}")

	debug_log("Exited extract_nav_metadata")
