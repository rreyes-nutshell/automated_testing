# ------------------------------
# db_inserter.py
# ------------------------------

from utils.db_utils import get_db_connection
from utils.logging import debug_log
import uuid

def insert_ui_path_item(ui_path_id, parent_id, seq, data):
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("""
		INSERT INTO ui_automation.ui_path_items (
			ui_path_id, parent_item_id, sequence_order,
			label, element_id, class_name, tag_name, name_attr,
			role, aria_label, aria_describedby,
			href, dest_url, xpath, css_selector,
			inner_text, outer_html, click_action, is_clickable,
			classification, created_by, crawler_session_id
		) VALUES (
			%(ui_path_id)s, %(parent_id)s, %(seq)s,
			%(label)s, %(element_id)s, %(class_name)s, %(tag_name)s, %(name_attr)s,
			%(role)s, %(aria_label)s, %(aria_describedby)s,
			%(href)s, %(dest_url)s, %(xpath)s, %(css_selector)s,
			%(inner_text)s, %(outer_html)s, %(click_action)s, %(is_clickable)s,
			NULL, 'crawler', %(ui_path_id)s
		) RETURNING id;
	""", {
		'ui_path_id': ui_path_id,
		'parent_id': parent_id,
		'seq': seq,
		**data
	})
	item_id = cur.fetchone()[0]
	conn.commit()
	cur.close()
	conn.close()
	return item_id

def insert_user_visible_path(username, item_id, crawl_session_id, visible=True, reason=None):
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("""
		INSERT INTO ui_automation.user_visible_paths (
			username, ui_path_item_id, crawl_session_id, visible, visibility_reason
		) VALUES (%s, %s, %s, %s, %s);
	""", (username, item_id, crawl_session_id, visible, reason))
	conn.commit()
	cur.close()
	conn.close()

def insert_ui_page_snapshot(ui_path_id, final_url, page_title, html_dump):
	from utils.logging import debug_log
	debug_log("Entered")
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("""
		INSERT INTO ui_automation.ui_page_snapshots (
			ui_path_id, final_url, page_title, html_dump, created_by
		) VALUES (%s, %s, %s, %s, %s);
	""", (ui_path_id, final_url, page_title, html_dump, 'crawler'))
	conn.commit()
	cur.close()
	conn.close()
	debug_log("Exited")


def insert_crawl_session(username, is_superuser, session_note):
	debug_log("Entered")
	crawl_uuid = str(uuid.uuid4())
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("""
		INSERT INTO ui_automation.ui_crawl_sessions (username, is_superuser, session_note, created_by, session_id)
		VALUES (%s, %s, %s, %s, %s)
		RETURNING id;
	""", (username, is_superuser, session_note, username, crawl_uuid))
	session_db_id = cur.fetchone()[0]
	conn.commit()
	cur.close()
	conn.close()
	debug_log("Exited")
	return session_db_id, crawl_uuid

def insert_ui_path(crawl_session_id, path_name):
	debug_log("Entered with path_name: " + path_name)
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("""
		INSERT INTO ui_automation.ui_paths (crawl_session_id, path_name, created_by)
		VALUES (%s, %s, %s)
		RETURNING id;
	""", (crawl_session_id, path_name, "crawler"))
	path_id = cur.fetchone()[0]
	conn.commit()
	cur.close()
	conn.close()
	debug_log("Exited")
	return path_id

# <<08-JUN-2025:14:28>> - Stubbed function to save UI page metadata into Postgres
# File: root/database/db_utils.py

async def save_ui_page_metadata(page, text: str, depth: int):
	debug_log("Entered")
	try:
		url = page.url
		title = await page.title()
		html = await page.content()

		conn = get_db_connection()
		cur = conn.cursor()

		sql = """
			INSERT INTO ui_automation.ui_pages (page_title, page_url, html_dump, nav_label, depth_level, creation_date)
			VALUES (%s, %s, %s, %s, %s, NOW())
		"""
		cur.execute(sql, (title, url, html, text, depth))
		conn.commit()
		cur.close()
		conn.close()

	except Exception as e:
		debug_log(f"❌ DB insert error in save_ui_page_metadata: {e}")

	debug_log("Exited")
# <<08-JUN-2025:21:53>> - Added to log UI sub-elements discovered during in-page crawling

# <<08-JUN-2025:22:42>> - insert_ui_element now auto-detects page_id from ui_pages
 

# <<09-JUN-2025:16:11>> - get_page_id_by_url now defined above insert_ui_element to avoid circular import

 

def get_page_id_by_url(page_url):
	debug_log("Entered")

	try:
		conn = get_db_connection()
		cursor = conn.cursor()
		cursor.execute("SELECT id FROM ui_pages WHERE url = %s", (page_url,))
		result = cursor.fetchone()
		cursor.close()
		conn.close()
		return result[0] if result else None

	except Exception as e:
		debug_log(f"Page ID lookup failed: {str(e)}")
		return None

	debug_log("Exited")

def insert_ui_element(element_data):
	debug_log("Entered")

	try:
		page_url = element_data.get("page_url")
		page_id = get_page_id_by_url(page_url)

		if not page_id:
			debug_log(f"Skipping insert: no page_id found for {page_url}")
			return

		conn = get_db_connection()
		cursor = conn.cursor()

		insert_query = """
			INSERT INTO ui_elements (
				page_id, page_url, label, tag_name, element_type,
				xpath, css_selector, session_id, created_at
			) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
		"""

		cursor.execute(insert_query, (
			page_id,
			page_url,
			element_data.get("label"),
			element_data.get("tag_name"),
			element_data.get("element_type"),
			element_data.get("xpath"),
			element_data.get("css_selector"),
			element_data.get("session_id")
		))

		conn.commit()
		debug_log(f"Inserted element: {element_data.get('label')} → {page_url}")

	except Exception as e:
		debug_log(f"DB Insert error: {str(e)}")

	finally:
		try:
			cursor.close()
			conn.close()
		except:
			pass

	debug_log("Exited")
