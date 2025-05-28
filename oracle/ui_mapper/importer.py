# ui_mapper/importer.py
import json

from datetime import datetime

from utils.logging import debug_log
from utils.db_utils import get_db_connection

import os

def import_jsonl_to_db(path, conn=None):
	if conn is None:
		conn = get_db_connection()
	debug_log("Entered")
	inserted = 0
	skipped = 0

	with open(path, "r") as f, conn.cursor() as cur:
		for line in f:
			try:
				data = json.loads(line.strip())

				page_name = data.get("label")
				url = data.get("url")
				selector = data.get("selector")
				page_id = data.get("page_id")
				category = data.get("category")
				version = data.get("version", "unknown")
				is_external = data.get("is_external", False)
				has_real_url = data.get("has_real_url", False)
				aria_label = data.get("aria_label")
				title_attr = data.get("title_attr")
				crawler_name = data.get("crawler_name")
				session_id = data.get("session_id")
				captured_at = data.get("captured_at")

				if not captured_at:
					captured_at = datetime.utcnow().isoformat()

				if not page_name or not selector:
					skipped += 1
					debug_log(f"⚠️ Skipping malformed line: {line.strip()}")
					continue

				cur.execute("""
						INSERT INTO ui_pages (
								page_name, page_id, url, selector, category, version, is_external,
								has_real_url, aria_label, title_attr, crawler_name, session_id,
								captured_at, created_by, last_updated_by
						)
						VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
						ON CONFLICT (page_name, url) DO NOTHING
				""", (
						page_name, page_id, url, selector, category, version, is_external,
						has_real_url, aria_label, title_attr, crawler_name, session_id,
						captured_at, 'importer', 'importer'
				))

				if cur.rowcount == 1:
					inserted += 1

			except Exception as e:
				skipped += 1
				debug_log(f"❌ Error: {e} — Line: {line.strip()}")

	conn.commit()
	debug_log(f"✅ Import complete — Inserted: {inserted}, Skipped: {skipped}")
	debug_log("Exited")
