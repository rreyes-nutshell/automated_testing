# ------------------------------
# db_inserter.py
# ------------------------------

from utils.db_utils import get_db_connection 
from utils.logging import debug_log
from typing import Optional

# <<09-JUN-2025:18:45>> - Updated for session_name model; removed crawler_session_id UUID

def insert_ui_path_item(ui_path_id, parent_id, seq, data, session_name):
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("""
		INSERT INTO ui_automation.ui_path_items (
			ui_path_id, parent_item_id, sequence_order,
			label, element_id, class_name, tag_name, name_attr,
			role, aria_label, aria_describedby,
			href, dest_url, xpath, css_selector,
			inner_text, outer_html, click_action, is_clickable,
			classification, created_by, session_name
		) VALUES (
			%(ui_path_id)s, %(parent_id)s, %(seq)s,
			%(label)s, %(element_id)s, %(class_name)s, %(tag_name)s, %(name_attr)s,
			%(role)s, %(aria_label)s, %(aria_describedby)s,
			%(href)s, %(dest_url)s, %(xpath)s, %(css_selector)s,
			%(inner_text)s, %(outer_html)s, %(click_action)s, %(is_clickable)s,
			NULL, 'crawler', %(session_name)s
		) RETURNING id;
	""", {
		'ui_path_id': ui_path_id,
		'parent_id': parent_id,
		'seq': seq,
		'session_name': session_name,
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

# <<09-JUN-2025:18:28>> - Inserts a new crawl session using session_name


# <<09-JUN-2025:12:30>> - Updated to require and store session_name instead of generating UUID

# <<09-JUN-2025:14:07>> - Insert only if session_name doesn't already exist
# <<10-JUN-2025:23:11>> - Prevent duplicate insert by checking existing session
def insert_crawl_session(session_name):
	debug_log("Entered")
	try:
		conn = get_db_connection()
		cur = conn.cursor()

		cur.execute("SELECT id FROM ui_automation.ui_crawl_sessions WHERE session_name = %s", (session_name,))
		existing = cur.fetchone()
		if existing:
			debug_log(f"⚠️ Session '{session_name}' already exists. Returning existing id: {existing[0]}")
			return existing[0]

		cur.execute("""
			INSERT INTO ui_automation.ui_crawl_sessions (session_name, created_at,started_at)
			VALUES (%s, now(), now()) RETURNING id
		""", (session_name,))
		session_id = cur.fetchone()[0]
		conn.commit()
		cur.close()
		conn.close()
		debug_log("Exited")
		return session_id

	except Exception as e:
		debug_log(f"insert_crawl_session failed: {e}")
		return None



# <<09-JUN-2025:18:42>> - Uses session_name instead of session_id
def insert_ui_path(session_name, path_name):
	debug_log("Entered")

	try:
		conn = get_db_connection()
		cursor = conn.cursor()

		cursor.execute("""
			INSERT INTO ui_automation.ui_paths (
				session_name, path, timestamp
			) VALUES (%s, %s, NOW())
			RETURNING id
		""", (session_name, path_name))

		result = cursor.fetchone()
		conn.commit()
		cursor.close()
		conn.close()
		return result[0]

	except Exception as e:
		debug_log(f"insert_ui_path error: {e}")
		return None

	debug_log("Exited")

# <<08-JUN-2025:14:28>> - Stubbed function to save UI page metadata into Postgres
# File: root/database/db_utils.py
# <<09-JUN-2025:18:28>> - Saves page info and associates with session_name
# <<09-JUN-2025:14:08>> - Updated to accept session_id and path_id explicitly
# <<09-JUN-2025:16:47>> - Updated to accept both session_id and session_name
# <<09-JUN-2025:16:56>> - Adjusted to accept correct params: page, session_id, session_name, path_id, page_url, label
def save_ui_page_metadata(
	page,
	session_id,
	session_name,
	path_id,
	page_url,
	page_title,
	page_heading,
	page_description
):
	debug_log("Entered")
	try:
		conn = get_db_connection()
		cur = conn.cursor()

		sql = """
			INSERT INTO ui_automation.ui_pages (
				session_id,
				session_name,
				path_id,
				url,
				page_title,
				page_heading,
				page_description,
				created_at
			) VALUES (
				%(session_id)s,
				%(session_name)s,
				%(path_id)s,
				%(url)s,
				%(page_title)s,
				%(page_heading)s,
				%(page_description)s,
				now()
			);
		"""

		params = {
			"session_id": session_id,
			"session_name": session_name,
			"path_id": path_id,
			"url": page_url,
			"page_title": page_title,
			"page_heading": page_heading,
			"page_description": page_description
		}

		cur.execute(sql, params)
		conn.commit()
		cur.close()
		conn.close()

		debug_log(f"UI page metadata saved: {session_name}, {page_url}, {page_heading}")
	except Exception as e:
		debug_log(f"DB Insert error in save_ui_page_metadata: {e}")
	debug_log("Exited")

# <<09-JUN-2025:13:13>> - Updated to use session_name for FK join to crawl_sessions

# <<09-JUN-2025:15:05>> - Full insert_ui_element with smart skip for unknown page_url
# <<09-JUN-2025:14:58>> - Added safe fallback for missing page URL entries and ensured robust insert
# <<09-JUN-2025:15:52>> - Enhanced insert_ui_element with deduping and fallback
# <<09-JUN-2025:15:15>> - Insert now gracefully skips missing pages, auto-filling from latest page in memory if applicable.
# <<09-JUN-2025:15:10>> - Enhanced with fallback logic and debug logging
# <<11-JUN-2025:20:55>> - Added aria_label and title_attr fields to insert_ui_element

def insert_ui_element(data: dict):
	debug_log("Entered insert_ui_element")
	try:
		page_id = get_page_id_by_context(
			session_id=data.get("session_id"),
			path_id=data.get("path_id"),
			page_url=data.get("page_url")
		)

		if page_id is None:
			debug_log(f"insert_ui_element error: No UI page found for context: session={data.get('session_id')} path={data.get('path_id')} url={data.get('page_url')}")
			return

		with get_db_connection() as conn:
			with conn.cursor() as cur:
				cur.execute(
					"""
					INSERT INTO ui_automation.ui_elements (
						page_id,
						session_id,
						label,
						tag_name,
						element_type,
						aria_label,
						title_attr,
						xpath,
						css_selector,
						created_at
					)
					VALUES (
						%(page_id)s,
						%(session_id)s,
						%(label)s,
						%(tag_name)s,
						%(element_type)s,
						%(aria_label)s,
						%(title_attr)s,
						%(xpath)s,
						%(css_selector)s,
						NOW()
					)
					""",
					{
						"page_id": page_id,
						"session_id": data.get("session_id"),
						"label": data.get("label"),
						"tag_name": data.get("tag_name"),
						"element_type": data.get("element_type"),
						"aria_label": data.get("aria_label"),  # new
						"title_attr": data.get("title_attr"),  # new
						"xpath": data.get("xpath"),
						"css_selector": data.get("css_selector")
					}
				)
				conn.commit()
	except Exception as e:
		debug_log(f"insert_ui_element error: {e}")
	debug_log("Exited insert_ui_element")




# <<09-JUN-2025:13:16>> - Moved from utils; utility to look up session_id by session_name
 
# <<09-JUN-2025:14:07>> - Fetch existing session ID by session name
def get_crawl_session_id_by_name(session_name):
	debug_log("Entered")
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("""
		SELECT id FROM ui_automation.ui_crawl_sessions
		WHERE session_name = %s
	""", (session_name,))
	row = cur.fetchone()
	cur.close()
	conn.close()
	debug_log("Exited")
	return row[0] if row else None

	if not result:
		raise LookupError(f"No crawl session found for name: {session_name}")

	debug_log("Exited get_crawl_session_id_by_name")
	return result[0]


# <<09-JUN-2025:13:16>> - Moved from utils; utility to look up page_id by page_url

def get_page_id_by_url(page_url):
	debug_log("Entered get_page_id_by_url")
	debug_log(f"Retrieving page_id for URL: {page_url}")
	if not page_url:
		debug_log("No page URL provided, cannot retrieve page_id.")
		raise ValueError("Page URL is required to retrieve page_id.")

	if not page_url:
		raise ValueError("Page URL is required to retrieve page_id.")

	conn = get_db_connection()
	cursor = conn.cursor()

	debug_log(f"[DEBUG] Looking up page_url: >>>{page_url}<<<")
	cursor.execute("SELECT page_url FROM ui_automation.ui_pages")
	rows = cursor.fetchall()
	for r in rows:
		debug_log(f"[DEBUG] DB row: >>>{r[0]}<<<")


	cursor.execute("""
		SELECT id FROM ui_automation.ui_pages
		WHERE url = %s
		LIMIT 1
	""", (page_url,))


	result = cursor.fetchone()
	debug_log(f"[DEBUG] DB row: >>>{result}<<<")

	# Diagnostic: list all rows if no match
	if not result:
		cursor.execute("SELECT id, page_url FROM ui_automation.ui_pages")
		all_rows = cursor.fetchall()
		debug_log("[DEBUG] Fallback full scan:")
		for r in all_rows:
			debug_log(f"  - ID: {r[0]} | URL: >>>{r[1]}<<<")
	cursor.close()
	conn.close()

	if result is None:
		debug_log(f"No page found for URL: {page_url}")
		debug_log("Exited get_page_id_by_url")
		raise LookupError(f"No UI page found for URL: {page_url}")
	
	if not result:
		debug_log(f"No page found for URL: {page_url}")
		raise LookupError(f"No UI page found for URL: {page_url}")

	debug_log("Exited get_page_id_by_url")
	return result[0]
# <<09-JUN-2025:15:54>> - Add to db_inserter.py
# <<09-JUN-2025:14:43>> - Added to resolve session_id from session_name for fallback UI element insert

def get_session_id_by_name(session_name: str):
	debug_log("Entered")
	try:
		with get_db_connection() as conn:
			with conn.cursor() as cur:
				cur.execute(
					"SELECT session_id FROM ui_automation.ui_crawl_sessions WHERE session_name = %s",
					(session_name,)
				)
				result = cur.fetchone()
				if result:
					return result[0]
	except Exception as e:
		debug_log(f"get_session_id_by_name error: {e}")
	debug_log("Exited")

def get_page_id_by_context(*, session_id: int, path_id: int, page_url: str) -> Optional[int]:
	try:
		conn = get_db_connection()
		cur = conn.cursor()
		cur.execute(
			"""
			SELECT id FROM ui_automation.ui_pages
			WHERE session_id = %s AND path_id = %s AND url = %s
			ORDER BY created_at DESC
			LIMIT 1
			""",
			(session_id, path_id, page_url)
		)
		row = cur.fetchone()
		cur.close()
		conn.close()
		return row[0] if row else None
	except Exception as e:
		debug_log(f"get_page_id_by_context error: {e}")
		return None

def insert_ui_page_trap(data: dict):
	debug_log("Entered insert_ui_page_trap")
	try:
		with get_db_connection() as conn:
			with conn.cursor() as cur:
				cur.execute(
					"""
					INSERT INTO ui_automation.ui_trap_pages (
						session_id, path_id, url, label, trap_reason, created_at
					)
					VALUES (
						%(session_id)s, %(path_id)s, %(url)s, %(label)s, %(trap_reason)s, NOW()
					)
					""",
					data
				)
				conn.commit()
	except Exception as e:
		debug_log(f"❌ Failed to insert trap page: {e}")
	debug_log("Exited insert_ui_page_trap")
