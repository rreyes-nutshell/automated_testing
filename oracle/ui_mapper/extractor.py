# ------------------------------
# extractor.py (entry point)
# ------------------------------

# <<10-JUN-2025:23:59>> - Restored full function and properly reintegrated extract_dom_info without placeholders
# <<10-JUN-2025:01:10>> - Added comment to guard modal dismiss from affecting legitimate nav containers
# <<10-JUN-2025:01:30>> - Refactored to defer modal dismissal and only trigger when visibly blocking
# <<10-JUN-2025:21:45>> - Added recursive subnav handling and improved in-page action coverage
# <<10-JUN-2025:23:59>> - Now performs click on each top-level nav item to initiate crawl
# <<11-JUN-2025:00:26>> - Added page wait and recursive crawl trigger for nav item clicks
# <<11-JUN-2025:01:19>> - Refreshed nav_items locator on each loop iteration to avoid stale DOM reference
# <<11-JUN-2025:02:20>> - Inserted hard reload of nav container before each click to ensure consistent selector behavior
# <<11-JUN-2025:03:10>> - Dumped visited set after each crawl_nav_items call for debugging

from oracle.ui_mapper.db_inserter import (
	insert_crawl_session,
	insert_ui_path,
	insert_ui_path_item,
	insert_user_visible_path
)
from oracle.ui_mapper.page_scanner import extract_page_contents
from oracle.ui_mapper.dom_extractor import extract_dom_info
from utils.logging import debug_log
from utils.modal_handler import dismiss_modal_if_present

__all__ = [
	"insert_crawl_session",
	"insert_ui_path",
	"extract_nav_metadata"
]

# ✅ Main extractor function
async def extract_nav_metadata(page, username: str, is_superuser: bool, session_note: str = None):
	from oracle.ui_mapper.recursive_crawler import crawl_nav_items

	session_id = insert_crawl_session(session_name=session_note)
	path_id = insert_ui_path(session_name=session_note, path_name="Top Nav Crawl")

	if not path_id:
		debug_log("❌ insert_ui_path failed, aborting nav item insert")
		return

	selector = "div[id*='_UISnvr'] a"
	count = await page.locator(selector).count()
	debug_log(f"📊 Found {count} top-level nav items")

	for i in range(count):
		try:
			await page.goto(page.url, timeout=15000)
			await page.wait_for_selector(selector, timeout=10000)

			nav_items = page.locator(selector)  # Refresh locator to avoid stale reference
			element = nav_items.nth(i)

			if not await element.is_visible():
				debug_log(f"⏭️ Skipping hidden item {i}")
				continue

			id_attr = await element.get_attribute("id")
			if not id_attr or "nvcl" in id_attr or "nvcil" in id_attr:
				continue

			href = await element.get_attribute("href")
			onclick = await element.get_attribute("onclick")
			if (not href or href.strip() == "#") and not onclick:
				continue

			# Ensure modal handler does not dismiss legitimate nav containers before this point
			dom_data = await extract_dom_info(element)
			item_id = insert_ui_path_item(
				path_id=path_id,
				parent_id=None,
				seq=i,
				data=dom_data,
				session_name=session_note
			)

			if not is_superuser:
				insert_user_visible_path(
					username=username,
					item_id=item_id,
					session_name=session_note,
					visible=True
				)

			# Modal dismiss only after interaction starts (safe zone)
			await dismiss_modal_if_present(page)

			# New: Trigger click to begin crawl into this section
			await element.scroll_into_view_if_needed()
			await element.click(timeout=5000)
			await page.wait_for_load_state("networkidle", timeout=10000)
			await page.wait_for_timeout(1000)

			visited = set()
			await crawl_nav_items(
				page=page,
				path_id=path_id,
				item_label=dom_data.get("label", f"nav_{i}"),
				visited=visited,
				session_id=session_id,
				session_name=session_note
			)

			debug_log(f"🧾 Visited after nav item {i}: {visited}")

		except Exception as e:
			debug_log(f"⚠️ Skipped nav item {i}: {e}")
			continue

	debug_log("Exited extract_nav_metadata")
