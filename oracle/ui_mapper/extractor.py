# extractor.py — Restored clean version for metadata extraction only
from utils.logging import debug_log
from utils.db_utils import get_db_connection
from playwright.sync_api import Page
from datetime import datetime

def insert_crawl_session(username, is_superuser, session_note):
	debug_log("Entered")
	import uuid
	crawl_uuid = str(uuid.uuid4())
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("""
		INSERT INTO ui_crawl_sessions (username, is_superuser, session_note, created_by, session_id)
		VALUES (%s, %s, %s, %s, %s)
		RETURNING id;
	""", (username, is_superuser, session_note, username, crawl_uuid))
	session_db_id = cur.fetchone()[0]
	conn.commit()
	cur.close()
	conn.close()
	debug_log("✅ Reached extract_page_contents call")
	debug_log("Exited")	
	return session_db_id, crawl_uuid

def insert_ui_path(crawl_session_id, path_name):
	debug_log("Entered")
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("""
		INSERT INTO ui_paths (crawl_session_id, path_name, created_by)
		VALUES (%s, %s, %s)
		RETURNING id;
	""", (crawl_session_id, path_name, "crawler"))
	path_id = cur.fetchone()[0]
	conn.commit()
	cur.close()
	conn.close()
	debug_log("Exited")
	return path_id


import os

async def extract_page_contents(page: Page, session_id: int, path_id: int):
	debug_log("Entered")
	await page.wait_for_timeout(3000)
	elements = page.locator("[role], [id], table, th, td, oj-table")
	count = await elements.count()
	debug_log(f"📄 Page DOM elements found: {count}")

	# Save a snapshot for debugging
	html = await page.content()
	snapshot_path = f"page_snapshot_session_{session_id}.html"
	with open(snapshot_path, "w", encoding="utf-8") as f:
		f.write(html)
	debug_log(f"📷 Saved HTML snapshot to: {snapshot_path}")

	# Log visible body text for quick inspection
	try:
		text_dump = await page.locator("body").inner_text()
		debug_log(f"📎 Body text sample: {text_dump[:200].replace('\\n', ' ').replace('\\r', '')}...")

	except Exception as e:
		debug_log(f"⚠️ Could not extract body text: {e}")

	# Check for iframes
	iframe_count = await page.locator("iframe").count()
	debug_log(f"🪟 Found {iframe_count} iframe(s) on the page")

	# Check for Oracle custom tags
	oracle_locator = page.locator("[data-afr-facetype], [id*='afr'], [class*='af_'], [role]")
	oracle_tags = await oracle_locator.all_text_contents()
	debug_log(f"🔎 Oracle tag sample count: {len(oracle_tags)}")
	count = await elements.count()

	for i in range(count):
		try:
			element = elements.nth(i)
			tag = await element.evaluate("el => el.tagName")
			if i < 5:
				debug_log(f"🔖 Element {i} tag: {tag}")
			if not await element.is_visible():
				continue
			dom_data = await extract_dom_info(element)
			insert_ui_path_item(path_id, parent_id=None, seq=i, data=dom_data)
		
		except Exception as e:
			debug_log(f"⚠️ Failed to extract element {i}: {e}")
			continue

	debug_log("Exited")

def insert_ui_path_item(ui_path_id, parent_id, seq, data):
	debug_log("Entered")
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("""
		INSERT INTO ui_path_items (
			ui_path_id, parent_item_id, sequence_order,
			label, element_id, class_name, tag_name, name_attr,
			role, aria_label, aria_describedby,
			href, dest_url, xpath, css_selector,
			inner_text, outer_html, click_action, is_clickable,
			classification, created_by
		) VALUES (
			%(ui_path_id)s, %(parent_id)s, %(seq)s,
			%(label)s, %(element_id)s, %(class_name)s, %(tag_name)s, %(name_attr)s,
			%(role)s, %(aria_label)s, %(aria_describedby)s,
			%(href)s, %(dest_url)s, %(xpath)s, %(css_selector)s,
			%(inner_text)s, %(outer_html)s, %(click_action)s, %(is_clickable)s,
			NULL, 'crawler'
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
	debug_log("Exited")
	return item_id

def insert_user_visible_path(username, item_id, crawl_session_id, visible=True, reason=None):
	debug_log("Entered")
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("""
		INSERT INTO user_visible_paths (
			username, ui_path_item_id, crawl_session_id, visible, visibility_reason
		) VALUES (%s, %s, %s, %s, %s);
	""", (username, item_id, crawl_session_id, visible, reason))
	conn.commit()
	cur.close()
	conn.close()
	debug_log("Exited")

async def extract_dom_info(el):
	try:
		label_text = await el.text_content()
	except Exception as e:
		debug_log(f"⚠️ Failed to get text content: {e}")
		return {}
	label_trimmed = label_text.strip() if label_text else None
	if label_trimmed and len(label_trimmed) > 100:
		label_trimmed = label_trimmed[:100] + '...'
	tag_name = await el.evaluate("el => el.tagName.toLowerCase()")
	if tag_name in ["script", "style", "meta", "br"]:
		return {}
	classification = "button" if tag_name == "button" else "link" if tag_name == "a" else "field" if tag_name == "input" else "container"
	return {
		'label': label_trimmed,
		'tag_name': tag_name,
		'element_id': await el.get_attribute("id"),
		'class_name': await el.get_attribute("class"),
		'name_attr': await el.get_attribute("name"),
		'role': await el.get_attribute("role"),
		'aria_label': await el.get_attribute("aria-label"),
		'aria_describedby': await el.get_attribute("aria-describedby"),
		'href': await el.get_attribute("href"),
		'dest_url': await el.get_attribute("href"),
		'xpath': await el.evaluate("node => node.getAttribute('id') ? 'a#' + node.getAttribute('id').replace(/:/g, '\:') : node.tagName.toLowerCase()"),
		'css_selector': await el.evaluate("node => node.tagName.toLowerCase() + (node.id ? '#' + node.id.replace(/:/g, '\:') : '')"),
		'inner_text': await el.inner_text() if hasattr(el, 'inner_text') else '',
		'outer_html': await el.evaluate("node => node.outerHTML"),
		'click_action': 'click',
		'classification': classification,
		'is_clickable': True,
	}

def insert_ui_page_snapshot(ui_path_id, final_url, page_title, html_dump):
	debug_log("Entered")
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("""
		INSERT INTO ui_page_snapshots (
			ui_path_id, final_url, page_title, html_dump, created_by
		) VALUES (%s, %s, %s, %s, %s);
	""", (ui_path_id, final_url, page_title, html_dump, 'crawler'))
	conn.commit()
	cur.close()
	conn.close()
	debug_log("Exited")

async def extract_nav_metadata(page: Page, username: str, is_superuser: bool, session_note: str = None):
	debug_log("Entered")
	session_db_id, _ = insert_crawl_session(username, is_superuser, session_note)
	path_id = insert_ui_path(session_db_id, path_name="Top Nav Crawl")

	nav_items = page.locator("a[id^='pt1:_UISnvr']")
	count = await nav_items.count()
	for i in range(count):
		try:
			element = nav_items.nth(i)
			if not await element.is_visible():
				continue
		except Exception as e:
			debug_log(f"⚠️ Skipped nav item {i}: {e}")
			continue
		id_attr = await element.get_attribute("id")
		if not id_attr or "nvcl" in id_attr or "nvcil" in id_attr:
			continue

		href = await element.get_attribute("href")
		onclick = await element.get_attribute("onclick")
		if (not href or href.strip() == "#") and not onclick:
			continue

		dom_data = await extract_dom_info(element)
		item_id = insert_ui_path_item(path_id, parent_id=None, seq=i, data=dom_data)
		if not is_superuser:
			insert_user_visible_path(username, item_id, session_db_id, visible=True)

	debug_log("Exited")
