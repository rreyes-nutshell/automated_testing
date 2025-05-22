# extractor.py — Updated to store literal Playwright selector, not nth locator
import asyncio
from playwright.async_api import async_playwright
from utils.logging import debug_log
from utils.db_utils import get_db_connection

async def extract_nav_metadata(session_id, page):
	debug_log("Entered")

	
	nav_items = page.locator("a[id^='pt1:_UISnvr']")
	count = await nav_items.count()

	conn = get_db_connection()
	cursor = conn.cursor()

	cursor.execute("DELETE FROM ui_pages WHERE session_id = %s", (session_id,))

	for i in range(count):
		element = nav_items.nth(i)
		href = await element.get_attribute("href")
		onclick = await element.get_attribute("onclick")
		id_attr = await element.get_attribute("id")

		# Skip empty or known structural elements
		if not id_attr or "nvcl" in id_attr or "nvcil" in id_attr:
			continue

		# If it's not actually clickable, skip it
		if (not href or href.strip() == "#") and not onclick:
			continue
		label = await element.inner_text()
		href = await element.get_attribute("href")
		id_attr = await element.get_attribute("id")
		if id_attr:
			# Build a direct ID-based selector string
			selector = f"a#{id_attr.replace(':', '\\:')}"
		else:
			selector = await element.evaluate("el => el.tagName.toLowerCase()")  # fallback: tag name only

		fallback_locator = None

		cursor.execute("""
			INSERT INTO ui_pages (
				session_id, page_name, url, locator, fallback_locator,
				category, page_id, aria_label, title_attr,
				creation_date, created_by, last_update_date, last_updated_by
			)
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, NOW(), %s)
		""", (
			session_id,
			label.strip(),
			href,
			selector,
			fallback_locator,
			await element.get_attribute("data-category"),
			await element.get_attribute("id"),
			await element.get_attribute("aria-label"),
			await element.get_attribute("title"),
			"system",
			"system"
		))

	conn.commit()
	cursor.close()
	conn.close()

	debug_log("Exited")
