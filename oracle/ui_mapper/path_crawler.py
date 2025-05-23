from utils.logging import debug_log
from utils.db_utils import get_db_connection
from oracle.login_steps import run_oracle_login_steps
from oracle.ui_mapper import extractor
from oracle.ui_mapper.db_writer import DBWriter
from playwright.async_api import async_playwright
from datetime import datetime
import os


async def crawl_path_from_selector(selector, username, password, login_url, crawler_name, session_id):
	debug_log("Entered")
	writer = DBWriter("oracle_ui_dump.jsonl")

	async with async_playwright() as p:
		browser = await p.chromium.launch(headless=os.getenv("HEADLESS", "true").lower() == "true")
		context = await browser.new_context()
		page = await context.new_page()

		await run_oracle_login_steps(page, login_url, username, password)

		try:
			debug_log(f"🔍 Navigating to selector: {selector}")
			await page.wait_for_selector(selector, timeout=15000)
			element = page.locator(selector)
			label_before_click = await element.inner_text()
			aria_label = await element.get_attribute("aria-label")
			title_attr = await element.get_attribute("title")
			debug_log(f"🔍 Found element: {label_before_click} (aria-label: {aria_label}, title: {title_attr})")

			try:
				debug_log("🔄 Attempting to click element")
				async with page.expect_navigation(wait_until="load", timeout=10000):
					debug_log("🔄 Waiting for navigation"	)
					await element.click()
					debug_log("🔄 Navigation completed")
			except Exception as nav_err:
				debug_log(f"⚠️ Navigation didn't happen: {nav_err}")
				await element.click()  # fallback click


			print("📍 Current URL:", page.url)

			# Optional UI metadata insert for selected item
			extracted = {
				"label": label_before_click,
				"selector": selector,
				"url": page.url,
				"category": "TBD",
				"page_id": None,
				"aria_label": aria_label,
				"title_attr": title_attr
			}
			debug_log(f"📍 Extracted metadata: {extracted}"	)

			if extracted:
				await writer.insert_entry({**extracted, "crawler_name": crawler_name, "session_id": session_id})

				with get_db_connection() as conn:
					debug_log("Inserting into DB")
					cur = conn.cursor()
					cur.execute(
						"""
						INSERT INTO ui_pages (
							page_name, selector, url, category, captured_at, page_id,
							crawler_name, session_id,
							is_external, has_real_url, aria_label, title_attr
						) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, false, false, %s, %s)
						""",
						(
							extracted["label"],
							extracted["selector"],
							extracted["url"],
							extracted["category"],
							datetime.utcnow(),
							extracted.get("page_id"),
							crawler_name,
							session_id,
							extracted.get("aria_label"),
							extracted.get("title_attr"),
						)
					)
					conn.commit()

			# Trigger full nav extraction
			path_id = extractor.insert_ui_path(session_id, path_name=extracted["label"] or "Unknown")
			await extractor.extract_page_contents(page, session_id, path_id)

		except Exception as e:
			debug_log(f"⚠️ Error navigating to selector: {e}")

		await browser.close()
	debug_log("Exited")
