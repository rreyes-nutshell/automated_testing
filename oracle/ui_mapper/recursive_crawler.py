# <<08-JUN-2025:14:08>> - Full file dump with Navigator fix and capture_screenshot fix
# File: root/oracle/ui_mapper/recursive_crawler.py
# <<08-JUN-2025:17:33>> - Needed for async sleep delays in click retries
import asyncio
import os
from playwright.async_api import Page
from utils.logging import debug_log, capture_screenshot, log_html_to_file
from utils.selector_resolver import get_selector
from oracle.ui_mapper.db_inserter import save_ui_page_metadata
# Expand the hamburger menu using stable get_by_role method# <<08-JUN-2025:14:39>> - Retry Navigator detection + fix screenshot call
# File: root/oracle/ui_mapper/recursive_crawler.py

# <<08-JUN-2025:14:47>> - Skip re-clicking Navigator if its content is already visible
# File: root/oracle/ui_mapper/recursive_crawler.py

# <<08-JUN-2025:15:01>> - Use "My Enterprise" or "Others" as expanded-menu indicators
# File: root/oracle/ui_mapper/recursive_crawler.py

# <<08-JUN-2025:15:44>> - Wait briefly if menu is already expanded
# File: root/oracle/ui_mapper/recursive_crawler.py

async def expand_hamburger_menu(page: Page, session_id="unknown"):
	debug_log("Entered")
	try:
		already_expanded = (
			await page.get_by_text("Collapse Tools").is_visible() or
			await page.get_by_text("Collapse Others").is_visible() or
			await page.get_by_text("Collapse My Enterprise").is_visible()
		)
		if already_expanded:
			debug_log("📂 Menu already expanded, skipping Navigator click.")
			await page.wait_for_timeout(1000)  # let DOM settle before crawling
			return

		# Proceed with retry logic to click Navigator
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

		show_more_link = page.get_by_role("link", name="Show More")
		if await show_more_link.is_visible():
			await show_more_link.click()
			await page.wait_for_timeout(1000)
			debug_log("📂 Clicked Show More")

	except Exception as e:
		debug_log(f"⚠️ Menu expansion failed: {e}")

	debug_log("Exited")


# Recursive nav item crawler
# <<08-JUN-2025:15:06>> - Full recursive crawl using stable click, re-expand logic
# File: root/oracle/ui_mapper/recursive_crawler.py
# <<08-JUN-2025:15:12>> - Skip "Home", "Show Less", and all "Collapse *" items
# File: root/oracle/ui_mapper/recursive_crawler.py
# <<08-JUN-2025:15:34>> - Updated with real click validation and safe skips
# File: root/oracle/ui_mapper/recursive_crawler.py

# <<08-JUN-2025:15:57>> - Rewritten to recurse into real Oracle nav trees, not flat list
# File: root/oracle/ui_mapper/recursive_crawler.py

# <<08-JUN-2025:16:06>> - Logs selector used per crawl depth
# File: root/oracle/ui_mapper/recursive_crawler.py
# <<08-JUN-2025:17:51>> - Fully recurses Navigator + in-page AFPanelBoxContent links
# File: root/oracle/ui_mapper/recursive_crawler.py

# <<08-JUN-2025:17:51>> - Fully recurses Navigator + in-page AFPanelBoxContent links
# File: root/oracle/ui_mapper/recursive_crawler.py

# <<08-JUN-2025:18:14>> - Full recursive + in-page Oracle menu crawler
# File: root/oracle/ui_mapper/recursive_crawler.py

# <<08-JUN-2025:18:21>> - Full depth-aware recursive crawler w/ Oracle-safe waits
# File: root/oracle/ui_mapper/recursive_crawler.py

# <<08-JUN-2025:18:26>> - Oracle-safe wait selectors + metadata guard
# File: root/oracle/ui_mapper/recursive_crawler.py

async def crawl_nav_items(page: Page, visited=None, depth=0, session_id="unknown"):
	debug_log("Entered")

	if visited is None:
		visited = set()

	try:
		selector = "a:visible" if depth == 0 else "li[role='treeitem'] >> a"
		debug_log(f"{'  ' * depth}📁 Using selector: {selector}")

		nav_links = page.locator(selector)
		count = await nav_links.count()
		debug_log(f"{'  ' * depth}🔍 Found {count} nav items at depth {depth}")

		for i in range(count):
			item = nav_links.nth(i)

			try:
				text = (await item.inner_text()).strip()
				href = await item.get_attribute("href")
				key = f"{text}|{href}"

				if (
					not text or
					text == "Home" or
					text == "Show Less" or
					text.startswith("Collapse") or
					text.upper().__contains__("INSTALLER") or
					text.upper().__contains__("HELP") or
					text in ["Analytics", "Product Management","Marketplace","Cloud Customer Connect", "Sign Out", "Google Chrome Help",
							"Reports and Analytics","Reports and Analytics", "Financial Reporting Center", "Getting Started","About This Application","Hide Help Icons"] or
					key in visited
				):
					continue

				visited.add(key)
				debug_log(f"{'  ' * depth}➡️ Visiting: {text}")

				await item.click(timeout=5000)
				await page.wait_for_timeout(500)
				await page.wait_for_load_state("domcontentloaded")

				# ✅ New: universal post-nav wait (removes AP1 assumption)
				await page.wait_for_selector("body table, div.x1gl, div.AFPanelBoxContent", timeout=5000)

				# ✅ Guard against navigation race
				try:
					await save_ui_page_metadata(page, text=text, depth=depth)
				except Exception as e:
					debug_log(f"{'  ' * depth}⚠️ Skipped metadata save due to DOM destruction: {e}")

				# ✅ Try in-page crawl if sub-links exist
				try:
					# await page.wait_for_selector("div.AFPanelBoxContent a.xn", timeout=7000)
					# sub_links = page.locator("div.AFPanelBoxContent a.xn")
					# count = await sub_links.count()
					# debug_log(f"{'  ' * depth}🧪 Sub-link count: {count}")
					await page.wait_for_selector("button, a[role='link'], table", timeout=5000)
					ui_buttons = page.locator("button, a[role='link']")
					count = await ui_buttons.count()
					debug_log(f"{'  ' * depth}🧪 Actionable UI element count: {count}")
					await crawl_in_page_actions(page, ui_buttons, visited, depth + 1)
				except Exception as e:
					debug_log(f"{'  ' * depth}❌ Sub-panel never loaded or timed out: {e}")

				await page.go_back()
				await page.wait_for_timeout(1500)
				await expand_hamburger_menu(page, session_id=session_id)

			except Exception as e:
				debug_log(f"{'  ' * depth}❌ Failed nav [{i}]: {e}")
				continue

	except Exception as outer:
		debug_log(f"❌ Crawl loop error: {outer}")

	debug_log("Exited")

async def begin_recursive_crawl(page: Page, username: str, session_id: str, crawler_name="default"):
	debug_log("Entered")

	try:
		await expand_hamburger_menu(page)
		await crawl_nav_items(page)

	except Exception as e:
		debug_log(f"❌ Crawler exception: {e}")
		await capture_screenshot(page, "expand_menu_failure", step_num=0)
		await log_html_to_file(page, session_id, "html_crawler_error")

	debug_log("Exited")

# <<08-JUN-2025:18:02>> - In-page sub-nav crawler for Payables/Invoices panels
# File: root/oracle/ui_mapper/recursive_crawler.py

async def crawl_in_page_sub_links(page: Page, sub_links, visited, depth):
	try:
		count = await sub_links.count()
		if count == 0:
			return

		debug_log(f"{'  ' * depth}📂 Found {count} sub-links — descending")

		for j in range(count):
			try:
				sub = sub_links.nth(j)
				sub_text = (await sub.inner_text()).strip()
				if sub_text and sub_text not in visited:
					visited.add(sub_text)
					debug_log(f"{'  ' * depth}↳ Visiting sub-link: {sub_text}")
					await sub.click()
					await page.wait_for_timeout(2000)
					await save_ui_page_metadata(page, text=sub_text, depth=depth)
					await page.go_back()
					await page.wait_for_timeout(1000)
			except Exception as e:
				debug_log(f"{'  ' * depth}❌ Failed sub-click [{j}]: {e}")

	except Exception as e:
		debug_log(f"{'  ' * depth}❌ Sub-link crawl failed: {e}")
# 
# ================================================
# <<08-JUN-2025:21:23>> - crawl_in_page_actions updated:
# - Added debug log to confirm CRAWLER_TIMEOUT from .env
# - Replaced Locator chains with explicit .nth(j)
# - Retained retry logic and is_visible check
# ================================================

import asyncio
import os
from utils.logging import debug_log
from playwright.async_api import Page, Keyboard

# /oracle/ui_mapper/recursive_crawler.py

BLACKLIST_LABELS = {
	"Hide Help Icons",
	"About This Application",
	"Getting Started",
	"Reports and Analytics",
	"Financial Reporting Center",
	"Sign Out",
	"Google Chrome Help",
	"Analytics",
	"Product Management",
	"Marketplace",
	"Cloud Customer Connect",
	"Settings and Actions",
	"Applications Help"
}

async def crawl_in_page_actions(page, ui_buttons, visited, depth):
	pad = '  ' * depth
	debug_log(f"{pad}Entered")

	# Exit modals/popups like 'Settings and Actions' if visible
	try:
		popup_title = await page.locator("text=Settings and Actions").is_visible()
		if popup_title:
			debug_log(f"{pad}🧱 Popup detected: Settings and Actions — attempting ESC close")
			await page.keyboard.press("Escape")
			await asyncio.sleep(0.5)
			return
	except Exception as e:
		debug_log(f"{pad}❌ Failed to detect/close Settings popup: {e}")

	# Phase 1 detection of interactive UI
	try:
		form_elements = await page.locator("input, select, textarea").all()
		search_buttons = await page.locator("button:has-text('Search'), a:has-text('Search')").all()
		debug_log(f"{pad}🗭 Found {len(form_elements)} form fields and {len(search_buttons)} search triggers")
		if form_elements or search_buttons:
			debug_log(f"{pad}⚠️  Detected potential data-driven UI — interaction may be required.")
	except Exception as e:
		debug_log(f"{pad}❌ Error during form/search detection: {e}")

	# Broaden element scan
	try:
		selector = (
			"button, a[role='link'], div[role='button'], span[role='button'], "
			"a[href], div[onclick], td[onclick], img[onclick], "
			"span[class*='icon'], div[class*='tile'], div[class*='box']"
		)
		elements = page.locator(selector)
		count = await elements.count()
		debug_log(f"{pad}🧪 Actionable UI element count: {count}")

		if count == 0:
			debug_log(f"{pad}⚠️ No actionable in-page elements found")
			return

		click_timeout = int(os.getenv("CRAWLER_TIMEOUT", "10000"))
		debug_log(f"{pad}🔑 Confirmed click_timeout = {click_timeout}ms from .env")

		for j in range(count):
			try:
				element = elements.nth(j)
				label = (await element.inner_text()).strip()

				if not label:
					debug_log(f"{pad}⏭️ Skipping unnamed element [#{j}]")
					continue

				if label in BLACKLIST_LABELS:
					debug_log(f"{pad}⏭️ Skipping blacklisted element: {label}")
					continue

				display_index = f"{j+1} of {count}"
				debug_log(f"{pad}➡️ {display_index} <<{label}>>")

				await element.scroll_into_view_if_needed()

				if not await element.is_visible():
					debug_log(f"{pad}⏭️ Element not visible at time of click: {label}")
					continue

				try:
					await element.click(timeout=click_timeout)
				except Exception as retry_e:
					debug_log(f"{pad}⏳ Retry clicking: {label}")
					await asyncio.sleep(1)
					await element.click(timeout=click_timeout)

				from oracle.ui_mapper.db_inserter import save_ui_page_metadata
				await save_ui_page_metadata(page, label, depth+1)

				await asyncio.sleep(1.5)
			except Exception as e:
				debug_log(f"{pad}❌ Failed to click sub-action [{j}] ({label}): {e}")

	except Exception as outer:
		debug_log(f"{pad}❌ Crawler loop error: {outer}")

	debug_log(f"{pad}Exited")
