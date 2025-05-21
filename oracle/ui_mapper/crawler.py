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

async def crawl_oracle_ui(username, password, crawler_name="default", session_id=None):
        debug_log("Entered")
        if session_id is None:
                session_id = str(uuid.uuid4())

        conn = get_db_connection()
        cur = conn.cursor()
        writer = DBWriter("oracle_ui_dump.jsonl")

	async with async_playwright() as p:
		browser = await p.chromium.launch(headless=os.getenv("HEADLESS", "true").lower() == "true")
		context = await browser.new_context()
		page = await context.new_page()

		login_url = "https://login-ibnijb-dev1.fa.ocs.oraclecloud.com"
		await run_oracle_login_steps(page, login_url, username, password)

		# await page.wait_for_selector("a")
		await page.wait_for_selector("a", state="attached", timeout=10000)

		nav_links = await page.query_selector_all("a")

		extracted = []
		for i, anchor in enumerate(nav_links):
			try:
				selector = f"a >> nth={i}"
				entry = await extract_nav_metadata(page, selector)
				if entry:
					extracted.append(entry)
					debug_log(f"✅ Extracted: {entry['label']}")
			except Exception as e:
				debug_log(f"⚠️ Error processing link {i}: {e}")

		await browser.close()

                cur = conn.cursor()
                for row in extracted:
                        await writer.insert_entry({**row, "crawler_name": crawler_name, "session_id": session_id})
                        cur.execute(
                                """
                                INSERT INTO ui_pages (
                                        page_name, selector, url, category, captured_at, page_id,
                                        crawler_name, session_id,
                                        is_external, has_real_url, aria_label, title_attr
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, false, false, %s, %s)
                                """,
                                (
                                        row["label"],
                                        row["selector"],
                                        row["url"],
                                        row["category"],
                                        datetime.utcnow(),
                                        row.get("page_id"),
                                        crawler_name,
                                        session_id,
                                        row.get("aria_label"),
                                        row.get("title_attr"),
                                ),
                        )
		conn.commit()
		cur.close()
		conn.close()
	debug_log("Exited")

if __name__ == "__main__":
	asyncio.run(crawl_oracle_ui("your_user", "your_pass"))
