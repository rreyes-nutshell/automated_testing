# <<08-JUN-2025:14:08>> - Full file dump with Navigator fix and capture_screenshot fix
# File: root/oracle/ui_mapper/recursive_crawler.py
# <<08-JUN-2025:17:33>> - Needed for async sleep delays in click retries
# <<09-JUN-2025:17:00>> - Force reset built-in shadowing 

import asyncio
import os
from utils.visited_debugger import dump_visited
from utils.html_utils import get_page_description,label_is_suspected_data_row
from playwright.async_api import Page
from utils.logging import debug_log, slugify
from utils.url_utils import get_stable_url_signature
from utils.selector_resolver import get_selector
from oracle.ui_mapper.db_inserter import save_ui_page_metadata, insert_ui_path, insert_ui_element, insert_ui_page_trap
from utils.skip_rules import should_skip_label
from oracle.ui_mapper.db_inserter import insert_crawl_session, get_crawl_session_id_by_name
from utils.modal_handler import dismiss_modal_if_present, dismiss_oracle_menu_overlay
from oracle.ui_mapper.burger_launcher import launch_next_unclicked_icon
from utils.nav_helpers import post_login_nav_ready
# from oracle.ui_mapper.recursive_crawler import crawl_nav_items, expand_hamburger_menu

  

# <<09-JUN-2025:17:04>> - Fix for str shadowing across Python versions
import builtins
str = builtins.str

# <<09-JUN-2025:14:07>> - Handles session creation by crawler_name, only if not already found
# <<12-JUN-2025:21:03>> - Added burgers_visited to support tracking clicked icons across recursive sessions

# <<13-JUN-2025:17:46>> - Added burger traversal loop with crawl_nav_items integration
# <<13-JUN-2025:18:22>> - Added URL change verification before triggering crawl_nav_items
# <<13-JUN-2025:19:21>> - Removed premature hamburger reopen before page crawl
# <<13-JUN-2025:19:56>> - Shared visited state and prevented redundant burger launches
# <<13-JUN-2025:20:13>> - Improved post-traversal menu reopen logic and step 2–4 flow
# <<13-JUN-2025:22:06>> - Added start_index resume to avoid re-launching same burger on every trap


async def begin_recursive_crawl(page: Page, crawler_name=None, burgers_visited=None):
	debug_log("Entered begin_recursive_crawl")

	if not crawler_name:
		debug_log("❌ No crawler_name provided — aborting.")
		debug_log("Exited begin_recursive_crawl")
		return

	# if burgers_visited is None:
	# 	burgers_visited = set()

	visited = {}
	start_index = 0  # 🧠 Start from index 0

	session_id = get_crawl_session_id_by_name(crawler_name)
	if not session_id:
		session_id = insert_crawl_session(session_name=crawler_name)

	if not session_id:
		debug_log("❌ Could not create crawl session — aborting.")
		debug_log("Exited begin_recursive_crawl")
		return

	debug_log(f"Using crawler_name: {crawler_name}")
	path_id = insert_ui_path(crawler_name, path_name="Full Recursive Crawl")

	await post_login_nav_ready(page=page, burgers_visited=burgers_visited)

	while True:
		item_label, start_index = await launch_next_unclicked_icon(
			page=page,
			burgers_visited=burgers_visited,
			start_index=start_index
		)

		if not item_label:
			debug_log("✅ All burger icons processed — exiting loop.")
			break

		if item_label in burgers_visited:
			debug_log(f"🛑 Icon '{item_label}' already marked visited — skipping.")
			continue

		await page.wait_for_timeout(1500)

		try:
			await crawl_nav_items(
				page=page,
				path_id=path_id,
				item_label=item_label,
				session_id=session_id,
				session_name=crawler_name,
				visited=visited,
				burgers_visited=burgers_visited
			)
		except Exception as trap_flag:
			if "TRAP_DETECTED" in str(trap_flag):
				debug_log("🛑 Trap triggered reset to homepage")
				await page.goto(os.getenv("ORA_URL"))
				await post_login_nav_ready(page=page, burgers_visited=burgers_visited)

	debug_log("Exited begin_recursive_crawl")





# Expand the hamburger menu using stable get_by_role method# <<08-JUN-2025:14:39>> - Retry Navigator detection + fix screenshot call
# File: root/oracle/ui_mapper/recursive_crawler.py

# <<08-JUN-2025:14:47>> - Skip re-clicking Navigator if its content is already visible
# File: root/oracle/ui_mapper/recursive_crawler.py

# <<08-JUN-2025:15:01>> - Use "My Enterprise" or "Others" as expanded-menu indicators
# File: root/oracle/ui_mapper/recursive_crawler.py

# <<08-JUN-2025:15:44>> - Wait briefly if menu is already expanded
# File: root/oracle/ui_mapper/recursive_crawler.py

# <<09-JUN-2025:13:40>> - Updated to include visibility check and retry logic for Navigator expansion
# <<13-JUN-2025:20:41>> - Improved hamburger expansion with icon reload wait and return signal
# <<13-JUN-2025:20:41>> - Improved hamburger expansion with icon reload wait and return signal

async def expand_hamburger_menu(page: Page, session_id="unknown"):
	debug_log("Entered")

	try:
		# Check if already expanded based on "Collapse" indicators
		already_expanded = (
			await page.get_by_text("Collapse Tools").is_visible() or
			await page.get_by_text("Collapse Others").is_visible() or
			await page.get_by_text("Collapse My Enterprise").is_visible()
		)
		if already_expanded:
			debug_log("📂 Menu already expanded, skipping Navigator click.")
			await page.wait_for_timeout(1000)
			debug_log("Exited")
			return True

		# Try up to 3 times to open Navigator
		retries = 3
		for attempt in range(retries):
			try:
				navigator_btn = page.get_by_role("link", name="Navigator")
				await navigator_btn.wait_for(state="visible", timeout=3000)
				await navigator_btn.click()
				await page.wait_for_timeout(1000)
				debug_log("📂 Clicked Navigator")
				break
			except Exception as retry_err:
				debug_log(f"Retry {attempt+1}/{retries} failed: {retry_err}")
				await page.wait_for_timeout(1000)
		else:
			raise TimeoutError("Navigator button never became visible.")

		# Try to expand Show More if available
		try:
			show_more_link = page.get_by_role("link", name="Show More")
			if await show_more_link.is_visible():
				await show_more_link.click()
				await page.wait_for_timeout(1000)
				debug_log("📂 Clicked Show More")
		except Exception as sm_err:
			debug_log(f"⚠️ Show More check failed: {sm_err}")

		# Wait for burger icon DOM to load
		await page.wait_for_selector("a[id^='pt1:_UISnvr']", timeout=1000)
		debug_log("🍔 Burger icons now visible")

	except Exception as e:
		debug_log(f"⚠️ Menu expansion failed: {e}")
		debug_log("Exited")
		return False

	debug_log("Exited")
	return True


# <<09-JUN-2025:17:15>> - Removed  usage from logging to avoid shadowed built-in crash

# <<09-JUN-2025:17:54>> - Added line-by-line debug tracing to isolate exact failure cause
# <<09-JUN-2025:17:58>> - Fixed page.url() bug, restored normal crawling with stable logging
# <<09-JUN-2025:18:32>> - Updated to use session_name instead of session_id
# <<09-JUN-2025:13:10>> - Updated to accept session_name not session_id
# <<09-JUN-2025:13:34>> - Crawl Oracle nav items and recursively trigger page-level scanning
# <<09-JUN-2025:16:56>> - Updated crawl_nav_items to restore filtering logic and enforce named parameters
# <<09-JUN-2025:17:04>> - Updated for named params, correct await, skip logic, and bug fixes
# <<10-JUN-2025:02:36>> - Added conditional expansion for nav widgets based on child visibility check
# <<10-JUN-2025:03:11>> - Patched to only mark label visited after confirmed submenu expansion click
# <<10-JUN-2025:03:11>> - Patched to only mark label visited after confirmed submenu expansion click
# <<10-JUN-2025:03:11>> - Patched to only mark label visited after confirmed submenu expansion click
# <<11-JUN-2025:05:19>> - Refined nav crawl logic to avoid re-clicking expanded items and properly defer visited population
# <<11-JUN-2025:05:19>> - Refined nav crawl logic to avoid re-clicking expanded items and properly defer visited population
# <<11-JUN-2025:05:02>> - Added smart visited handling and skip expanded nodes

# <<11-JUN-2025:00:58>> - Added extra debug and click fallback logic to improve recursive crawling depth and modal interference handling# <<11-JUN-2025:17:00>> - Patched to use combined key of stable_url + page heading to scope visited set properly
# <<11-JUN-2025:18:30>> - Matched crawl_nav_items to use same visited namespacing as crawl_in_page_actions
# <<11-JUN-2025:19:45>> - Synced modal handling and visited labeling with latest recursion logic
# <<11-JUN-2025:17:00>> - Patched to use combined key of stable_url + page heading to scope visited set properly
# <<11-JUN-2025:18:30>> - Matched crawl_nav_items to use same visited namespacing as crawl_in_page_actions
# <<11-JUN-2025:19:45>> - Synced modal handling and visited labeling with latest recursion logic
# <<11-JUN-2025:21:00>> - Added DOM snapshot archival using page.content() per page navigation
# ------------------------------
# recursive_crawler.py - crawl_nav_items debug instrumentation
# ------------------------------
async def crawl_nav_items(
	page,
	path_id,
	item_label,
	visited,
	depth=0,
	session_id="unknown",
	session_name="unknown",
	burgers_visited=None
):
	debug_log(f"🔍 crawl_nav_items START for: {item_label}")

	burgers_visited = burgers_visited or set()

	selector = "a:visible"
	nav_items = page.locator(selector)
	count = await nav_items.count()
	debug_log(f"{'  ' * depth}🔍 Found {count} nav items at depth {depth}")

	page_url = page.url
	stable_url = get_stable_url_signature(page_url)

	page_heading = None
	try:
		h_el = await page.query_selector("h1, h2")
		if h_el:
			page_heading = await h_el.inner_text()
	except:
		pass

	heading_key = f"{stable_url}::{page_heading or 'unknown'}"

	if heading_key in visited and visited[heading_key]:
		debug_log(f"🛑 Page '{heading_key}' already visited — skipping.")
		return

	visited.setdefault(heading_key, set())

	save_ui_page_metadata(
		page=page,
		session_name=session_name,
		path_id=path_id,
		page_url=stable_url,
		page_title=item_label,
		page_heading=page_heading,
		page_description=None,
		session_id=session_id
	)

	try:
		html = await page.content()
		from pathlib import Path
		Path("dom_dumps").mkdir(parents=True, exist_ok=True)
		slug = slugify(page_heading or stable_url)
		with open(f"dom_dumps/{session_id}_{slug}.html", "w") as f:
			f.write(html)
		debug_log(f"📝 Saved DOM for: {page_heading or stable_url}")
	except Exception as snap_err:
		debug_log(f"❌ Failed DOM snapshot: {snap_err}")

	if item_label and item_label not in burgers_visited:
		burgers_visited.add(item_label)
		debug_log(f"📓 burgers_visited updated: {sorted(list(burgers_visited))}")

	# existing loop to crawl nav items...

	for i in range(count):
		try:
			element = nav_items.nth(i)
			text = await element.inner_text()
			label = text.strip()

			if should_skip_label(label, visited=visited[heading_key]):
				continue

			child_panel = element.locator("xpath=..//following-sibling::div[contains(@class, 'subnav')]")
			if await child_panel.is_hidden():
				debug_log(f"{'  ' * depth}⎵ Expanding: {label}")
				await dismiss_modal_if_present(page)
				await element.scroll_into_view_if_needed()
				await element.wait_for(state="visible", timeout=5000)
				await element.click(timeout=5000)
				await dismiss_modal_if_present(page)
				await page.wait_for_timeout(1000)
				visited[heading_key].add(label)
			else:
				debug_log(f"{'  ' * depth}⏭️ Already expanded: {label}")
				continue

			debug_log(f"{'  ' * depth}🧪 [TEST] checking in-page actions...")
			locator = page.locator("button:visible, a:visible, input:visible")
			count_actions = await locator.count()
			debug_log(f"{'  ' * depth}🧪 Actionable UI element count: {count_actions}")

			await dismiss_modal_if_present(page)

			try:
				await crawl_in_page_actions(
					page=page,
					session_id=session_id,
					session_name=session_name,
					page_url=page_url,
					stable_url=stable_url,
					locator=locator,
					visited=visited,
					path_id=path_id,
					burgers_visited=burgers_visited
				)

			except Exception as trap_flag:
				if "TRAP_DETECTED" in str(trap_flag):
					debug_log("🛑 Trap triggered reset to homepage")
					await page.goto(os.getenv("ORA_URL"))  # << same as login redirect
					await post_login_nav_ready(page)

			await dismiss_modal_if_present(page)

		except Exception as crawl_err:
			debug_log(f"{'  ' * depth}❌ Sub-panel error: {crawl_err}")

	if len(page.context.pages) > 1:
		try:
			original = page.context.pages[0]
			debug_log(f"📑 Closing tab: {page.url}")
			await page.close()
			page = original
		except Exception as tab_err:
			debug_log(f"⚠️ Failed to close extra tab: {tab_err}")

	dump_visited(visited)
	debug_log(f"✅ crawl_nav_items END for: {item_label}")

# 
# ================================================
# <<08-JUN-2025:21:31>> - crawl_in_page_actions patched for:
# - Broader element targeting
# - Pre-click logging
# - Skip-logging
# - Scroll-to-view fix
# - Popup exit protection for Settings & Actions
# - Remaining element countdown per page
# - Skip blacklist labels
# - Click timeout configurable via CRAWLER_TIMEOUT
# - Added is_visible() check before click
# - Retry logic on click failure
# - Call save_ui_page_metadata() with label, selector, depth, session_id
# ================================================



# /oracle/ui_mapper/recursive_crawler.py

# BLACKLIST_LABELS = {
# 	"Hide Help Icons",
# 	"About This Application",
# 	"Getting Started",
# 	"Reports and Analytics",
# 	"Financial Reporting Center",
# 	"Sign Out",
# 	"Google Chrome Help",
# 	"Analytics",
# 	"Product Management",
# 	"Marketplace",
# 	"Cloud Customer Connect",
# 	"Settings and Actions",
# 	"Applications Help"
# }

# <<09-JUN-2025:16:28>> - Patched for correct use of insert_ui_element() and defined page_url
 

# <<09-JUN-2025:16:44>> - Accepts 4 arguments and calls insert_ui_element() with full metadata
# <<09-JUN-2025:17:38>> - Patched to safely evaluate window.getXPath() and avoid str call crash
# <<09-JUN-2025:18:02>> - Fixed Locator count error; restored full crawling logic with XPath protection
# <<09-JUN-2025:18:26>> - Uses session_name in insert logic


# <<09-JUN-2025:13:12>> - Updated to use session_name instead of session_id
# <<09-JUN-2025:13:12>> - Updated to use session_name instead of session_id
# <<09-JUN-2025:13:34>> - Crawl all interactive elements on a subpage for LLM mapping
# <<09-JUN-2025:15:54>> - Full crawl_in_page_actions with timeout and element insert logic
# <<09-JUN-2025:18:38>> - Hardened crawl_in_page_actions to avoid flooding errors and support robust skipping.
# <<10-JUN-2025:21:12>> - Oracle modal detection and dismissal helper
# <<10-JUN-2025:21:12>> - Added modal recovery logic after each element click
# <<10-JUN-2025:22:02>> - Added overlay center-click dismiss for Oracle menu overlays
from utils.modal_handler import dismiss_modal_if_present, dismiss_oracle_menu_overlay
# <<11-JUN-2025:17:00>> - Patched to use combined key of stable_url + page heading to scope visited set properly
# <<11-JUN-2025:20:01>> - Added UI page metadata save inside crawl_in_page_actions()

# <<11-JUN-2025:20:15>> - Final patched version with fallback click and locator logging

# <<11-JUN-2025:20:48>> - Full function with aria-label/title patch, pre-click metadata logging

# <<11-JUN-2025:21:07>> - Trap screen skip logic added for data row drilldowns

# <<11-JUN-2025:21:34>> - Rewritten to detect trap screens after clicking

async def crawl_in_page_actions(page, session_id, session_name, page_url, stable_url, locator, visited, path_id,burgers_visited=None):  # <- add this line):
	debug_log("Entered")

	CRAWLER_TIMEOUT = int(os.getenv("CRAWLER_TIMEOUT", "5000"))
	MAX_ELEMENTS_PER_PAGE = int(os.getenv("MAX_ELEMENTS_PER_PAGE", "700"))

	page_heading = None
	try:
		h_el = await page.query_selector("h1, h2")
		if h_el:
			page_heading = await h_el.inner_text()
	except:
		pass

	heading_key = f"{stable_url}::{page_heading or 'unknown'}"

	if heading_key not in visited:
		visited[heading_key] = set()

	try:
		page_title = await page.title()
		page_description = await get_page_description(page)
		debug_log(f"📥 Saving metadata (in-page): {page_url} — {page_heading}")
		save_ui_page_metadata(
			page=page,
			session_id=session_id,
			session_name=session_name,
			path_id=path_id,
			page_url=page_url,
			page_title=page_title,
			page_heading=page_heading,
			page_description=page_description
		)
	except Exception as meta_err:
		debug_log(f"❌ Metadata save failed in crawl_in_page_actions: {meta_err}")

	try:
		locator_texts = await locator.all_text_contents()
		debug_log(f"📋 Locator text snapshot (first 5): {locator_texts[:5]}")
	except Exception as log_err:
		debug_log(f"⚠️ Couldn't log locator contents: {log_err}")

	try:
		total_count = await locator.count()
		count = min(total_count, MAX_ELEMENTS_PER_PAGE)
		debug_log(f"🕪 Actionable UI element count: {total_count} (processing max {count})")
	except Exception as count_err:
		debug_log(f"⚠️ Failed to count elements: {count_err}")
		debug_log("Exited")
		return

	for i in range(count):
		try:
			element = locator.nth(i)
			try:
				if not await element.is_visible() or not await element.is_enabled():
					debug_log(f"  ⏭️ Skipping element [{i}] — not visible or not enabled")
					continue

				label = await element.inner_text(timeout=CRAWLER_TIMEOUT)
				label = label.strip() if label else None
			except Exception as inner_err:
				debug_log(f"  ⏭️ Skipping element [{i}] — inner_text failed: {inner_err}")
				continue

			if not label or label in visited[heading_key]:
				continue

			if should_skip_label(label=label, visited=visited[heading_key]):
				debug_log(f"  ⏭️ Skipping blacklisted label: {label}")
				continue

			debug_log(f"➡️ Visiting nav item: {label}")

			await dismiss_modal_if_present(page=page)

			aria_label = await element.get_attribute("aria-label")
			title_attr = await element.get_attribute("title")

			try:
				await element.scroll_into_view_if_needed(timeout=CRAWLER_TIMEOUT)
				await element.click(timeout=CRAWLER_TIMEOUT, force=True)
			except Exception as click_err:
				debug_log(f"❌ Standard click failed for [{label}]: {click_err}")
				try:
					box = await element.bounding_box()
					if box:
						await page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
						debug_log("✅ Fallback mouse click succeeded")
					else:
						await element.dispatch_event("click")
						debug_log("✅ Dispatch event click fallback succeeded")
				except Exception as fallback_err:
					debug_log(f"❌ All fallback click methods failed: {fallback_err}")
					continue

			await dismiss_modal_if_present(page=page)
			await dismiss_oracle_menu_overlay(page=page)

			try:
				no_title = not await page.query_selector("h1, h2")
				no_nav = await page.locator("aside, nav").count() == 0
				no_actions = await page.locator("button, a").count() < 3

				debug_log(f"🛡️ Trap check — no_title: {no_title}, no_nav: {no_nav}, no_actions: {no_actions}")

				if no_nav and sum([no_title, no_actions]) >= 1:
					debug_log(f"🔒 Partial trap detected (missing nav): {page.url} (label: {label})")
					insert_ui_page_trap({
						"session_id": session_id,
						"path_id": path_id,
						"url": page.url,
						"label": label,
						"trap_reason": "Partial: No nav, plus missing title or actions"
					})
					await dismiss_modal_if_present(page)
					await dismiss_oracle_menu_overlay(page)
					raise Exception("TRAP_DETECTED")

					
			except Exception as trap_err:
				debug_log(f"⚠️ Trap check error: {trap_err}")

			visited[heading_key].add(label)

			insert_ui_element({
				"session_id": session_id,
				"page_url": stable_url,
				"label": label,
				"tag_name": await element.evaluate("e => e.tagName"),
				"element_type": await element.get_attribute("type"),
				"aria_label": aria_label,
				"title_attr": title_attr,
				"xpath": None,
				"css_selector": None,
				"path_id": path_id
			})

			await page.wait_for_timeout(1000)

		except Exception as click_err:
			await dismiss_modal_if_present(page=page)
			debug_log(f"  ❌ Failed to click sub-action [{i}] ({label or ''}): {click_err}")
			continue

	await dismiss_modal_if_present(page=page)
	await dismiss_oracle_menu_overlay(page=page)
	dump_visited(visited)
	debug_log("Exited")
