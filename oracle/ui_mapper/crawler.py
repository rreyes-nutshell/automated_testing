from utils.logging import debug_log
from utils.db_utils import get_db_connection
from oracle.login_steps import run_oracle_login_steps
from oracle.ui_mapper.extractor import extract_nav_metadata
from oracle.ui_mapper.db_writer import DBWriter
from playwright.async_api import async_playwright
import asyncio
import os
from datetime import datetime
import uuid

async def crawl_oracle_ui(username, password, crawler_name="default", session_id=None, login_url=None):

	debug_log("Entered")
	if session_id is None:
		session_id = str(uuid.uuid4())

	conn = get_db_connection()
	cur = conn.cursor()
	writer = DBWriter("oracle_ui_dump.jsonl")

	async with async_playwright() as p:
		browser = await p.chromium.launch(
			headless=os.getenv("HEADLESS", "true").lower() == "true"
		)
		context = await browser.new_context()
		page = await context.new_page()
		username = "mgonzalez@mfa.org"
		password = "Welcome!23"
		login_url = "https://login-ibnijb-dev1.fa.ocs.oraclecloud.com"
		# await run_oracle_login_steps(page, username, password, login_url)
		await run_oracle_login_steps(page, login_url, username, password)

		debug_log("Logged in")

		await extract_nav_metadata(session_id, page)

		# Confirm DB state
		cur.execute("SELECT page_name, locator FROM ui_pages WHERE session_id = %s", (session_id,))
		nav_links = cur.fetchall()
		extracted = []

		for i, row in enumerate(nav_links):
			try:
				label, selector = row
				debug_log(f"Trying selector: {selector}")
				element = page.locator(selector)
				await element.wait_for(state="attached", timeout=5000)
				await element.click()
				await asyncio.sleep(1)
				extracted.append({"label": label, "selector": selector})
				debug_log(f"✅ Clicked {label}")
			except Exception as e:
				debug_log(f"⚠️ Error processing link {i}: {e}")

		await browser.close()

		# Save extracted click results
		for row in extracted:
			await writer.insert_entry({
				**row,
				"crawler_name": crawler_name,
				"session_id": session_id,
			})
			cur.execute("""
				INSERT INTO ui_pages (
					page_name, selector, url, category, captured_at, page_id,
					crawler_name, session_id, is_external, has_real_url, aria_label, title_attr
				) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, false, false, %s, %s)
			""", (
				row["label"], row["selector"], None, None, datetime.utcnow(), None,
				crawler_name, session_id, None, None
			))

		conn.commit()
		cur.close()
		conn.close()
	debug_log("Exited")

if __name__ == "__main__":
	asyncio.run(crawl_oracle_ui("your_user", "your_pass"))
