from utils.logging import debug_log
from utils.db_utils import get_db_connection
from oracle.login_steps import run_oracle_login_steps
from oracle.ui_mapper.extractor import extract_nav_metadata
from playwright.async_api import async_playwright
import asyncio
import os
from datetime import datetime

async def crawl_oracle_ui(username, password):
        """Login to Oracle and capture navigation metadata."""
        debug_log("Entered")

        conn = get_db_connection()
        cur = conn.cursor()

        # Clear existing data so each crawl is fresh
        cur.execute("DELETE FROM ui_pages")
        cur.execute("DELETE FROM ui_map")
        conn.commit()
        cur.close()

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
                        # Persist basic page metadata
                        cur.execute(
                                """
                                INSERT INTO ui_pages (
                                        page_name, selector, url, category, captured_at, page_id,
                                        is_external, has_real_url, aria_label, title_attr
                                ) VALUES (%s, %s, %s, %s, %s, %s, false, false, NULL, %s)
                                """,
                                (
                                        row["label"], row["selector"], row["url"], row["category"],
                                        datetime.utcnow(), row.get("page_id"), row.get("page_title")
                                )
                        )

                        # Store selector details used for navigation
                        cur.execute(
                                """
                                INSERT INTO ui_map (
                                        label, parent_label, selector, page_id, action_type, value,
                                        url, category, is_actionable, created_by, last_updated_by
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'crawler', 'crawler')
                                ON CONFLICT (page_id) DO UPDATE
                                    SET selector = EXCLUDED.selector,
                                        url = EXCLUDED.url,
                                        last_update_date = CURRENT_TIMESTAMP,
                                        last_updated_by = 'crawler'
                                """,
                                (
                                        row["label"],
                                        row.get("parent_label"),
                                        row["selector"],
                                        row.get("page_id"),
                                        row.get("action_type"),
                                        row.get("value"),
                                        row["url"],
                                        row["category"],
                                        row.get("is_actionable", True),
                                )
                        )

                conn.commit()
                cur.close()
                conn.close()
	debug_log("Exited")

if __name__ == "__main__":
	asyncio.run(crawl_oracle_ui("your_user", "your_pass"))
