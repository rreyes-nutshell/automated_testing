# ------------------------------
# nav_crawler.py
# ------------------------------

from utils.logging import debug_log
from .db_inserter import insert_ui_path_item, insert_user_visible_path, insert_crawl_session, insert_ui_path
from .dom_extractor import extract_dom_info

async def extract_nav_metadata(page, username: str, is_superuser: bool, session_note: str = None):
	debug_log("Entered")
	session_db_id, _ = insert_crawl_session(username, is_superuser, session_note)
	path_id = insert_ui_path(session_db_id, path_name="Top Nav Crawl")

	nav_items = page.locator("a[id^='pt1:_UISnvr']")
	count = await nav_items.count()
	for i in range(count):
		try:
			element = nav_items.nth(i)
			if not await element.is_visible():
				continue
		except Exception as e:
			debug_log(f"⚠️ Skipped nav item {i}: {e}")
			continue
		id_attr = await element.get_attribute("id")
		if not id_attr or "nvcl" in id_attr or "nvcil" in id_attr:
			continue

		href = await element.get_attribute("href")
		onclick = await element.get_attribute("onclick")
		if (not href or href.strip() == "#") and not onclick:
			continue

		dom_data = await extract_dom_info(element)
		item_id = insert_ui_path_item(path_id, parent_id=None, seq=i, data=dom_data)
		if not is_superuser:
			insert_user_visible_path(username, item_id, session_db_id, visible=True)

	debug_log("Exited")

