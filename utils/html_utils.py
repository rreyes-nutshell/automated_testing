# utils/html_utils.py
from slugify import slugify
from utils.logging import debug_log
async def save_dom_snapshot(page, session_id, stable_url, page_heading):
	try:
		html = await page.content()
		with open(f"dom_dumps/{session_id}_{slugify(page_heading)}.html", "w") as f:
			f.write(html)
		debug_log(f"📝 Saved DOM for: {page_heading}")
	except Exception as e:
		debug_log(f"❌ Failed DOM snapshot: {e}")
# 
# <<11-JUN-2025:20:08>> - Fallback page description extractor
async def get_page_description(page):
	try:
		desc_el = await page.query_selector("meta[name='description']")
		if desc_el:
			return await desc_el.get_attribute("content")
	except:
		pass
	return None
# <<11-JUN-2025:21:13>> - Detects data table rows based on numeric-heavy labels
# <<11-JUN-2025:21:25>> - Improved to avoid flagging dashboard labels with counts

def label_is_suspected_data_row(label: str) -> bool:
	if not label:
		return False

	label = label.strip()

	# Skip short or clearly dashboard-style items
	if label.startswith("Item:") or label.startswith("Selected Item:"):
		return False

	# Table-like numeric rows: all digits or long PO style
	if label.replace(",", "").replace(" ", "").isdigit() and len(label) > 6:
		return True

	# Heuristic: long-ish, high digit density, not title cased
	if len(label) > 30:
		digit_ratio = sum(c.isdigit() for c in label) / len(label)
		if digit_ratio > 0.4:
			return True

	return False
