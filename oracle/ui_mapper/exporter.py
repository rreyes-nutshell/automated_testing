# ui_mapper/exporter.py
import json
from utils.logging import debug_log

def export_db_to_jsonl(path, conn):
	debug_log("Entered")
	cur = conn.cursor()
	cur.execute("""
		SELECT page_name, selector, url, category, captured_at, page_id,
		       is_external, has_real_url, aria_label, title_attr
		FROM ui_pages
		WHERE is_skipped = false
		ORDER BY page_name
	""")
	rows = cur.fetchall()
	cur.close()

	with open(path, "w") as f:
		for row in rows:
			data = {
				"label": row[0],
				"selector": row[1],
				"url": row[2],
				"category": row[3],
				"captured_at": row[4].isoformat() if row[4] else None,
				"page_id": row[5],
				"is_external": row[6],
				"has_real_url": row[7],
				"aria_label": row[8],
				"title_attr": row[9]
			}
			f.write(json.dumps(data) + "\n")

	debug_log(f"✅ Exported {len(rows)} records to {path}")
	debug_log("Exited")
