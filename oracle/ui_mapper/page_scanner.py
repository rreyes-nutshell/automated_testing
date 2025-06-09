# ------------------------------
# page_scanner.py
# ------------------------------

from utils.logging import debug_log
from .dom_extractor import extract_dom_info
from .db_inserter import insert_ui_path_item

async def extract_page_contents(page, session_id: int, path_id: str):
	debug_log("Entered")
	await page.wait_for_timeout(3000)
	elements = page.locator("[role], [id], table, th, td, oj-table")
	count = await elements.count()
	debug_log(f"📄 Page DOM elements found: {count}")

	html = await page.content()
	snapshot_path = f"page_snapshot_session_{session_id}.html"
	with open(snapshot_path, "w", encoding="utf-8") as f:
		f.write(html)
	debug_log(f"📷 Saved HTML snapshot to: {snapshot_path}")

	try:
		text_dump = await page.locator("body").inner_text()
		dump_clean = text_dump[:200].replace('\n', ' ').replace('\r', '')
		debug_log(f"📎 Body text sample: {dump_clean}...")
	except Exception as e:
		debug_log(f"⚠️ Could not extract body text: {e}")

	iframe_count = await page.locator("iframe").count()
	debug_log(f"🪟 Found {iframe_count} iframe(s) on the page")

	oracle_locator = page.locator("[data-afr-facetype], [id*='afr'], [class*='af_'], [role]")
	oracle_tags = await oracle_locator.all_text_contents()
	debug_log(f"🔎 Oracle tag sample count: {len(oracle_tags)}")

	for i in range(count):
		try:
			element = elements.nth(i)
			tag = await element.evaluate("el => el.tagName")
			if i < 5:
				debug_log(f"🔖 Element {i} tag: {tag}")
			if not await element.is_visible():
				continue
			dom_data = await extract_dom_info(element)
			insert_ui_path_item(path_id, parent_id=None, seq=i, data=dom_data)
		except Exception as e:
			debug_log(f"⚠️ Failed to extract element {i}: {e}")
			continue

	debug_log("Exited")
