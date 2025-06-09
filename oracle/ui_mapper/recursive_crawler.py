# <<08-JUN-2025:14:08>> - Full file dump with Navigator fix and capture_screenshot fix
# File: root/oracle/ui_mapper/recursive_crawler.py
# <<08-JUN-2025:17:33>> - Needed for async sleep delays in click retries
# <<09-JUN-2025:17:00>> - Force reset built-in shadowing 

import asyncio
import os
from playwright.async_api import Page
from utils.logging import debug_log, capture_screenshot, log_html_to_file
from utils.selector_resolver import get_selector
from oracle.ui_mapper.db_inserter import save_ui_page_metadata

# <<09-JUN-2025:17:04>> - Fix for str shadowing across Python versions
import builtins
str = builtins.str


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
# <<09-JUN-2025:17:15>> - Removed str() usage from logging to avoid shadowed built-in crash

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

				await page.wait_for_selector("body table, div.x1gl, div.AFPanelBoxContent", timeout=5000)

				# ✅ Inject XPath helper JS
				await page.evaluate("""
				window.getXPath = function(el) {
					if (!el || el.nodeType !== 1) return '';
					const parts = [];
					while (el && el.nodeType === 1) {
						let index = 1;
						let sibling = el.previousSibling;
						while (sibling) {
							if (sibling.nodeType === 1 && sibling.tagName === el.tagName) index++;
							sibling = sibling.previousSibling;
						}
						parts.unshift(el.tagName + '[' + index + ']');
						el = el.parentNode;
					}
					return '/' + parts.join('/');
				};
				""")

				try:
					await save_ui_page_metadata(page, text=text, depth=depth)
				except Exception as err:
					debug_log(f"{'  ' * depth}⚠️ Skipped metadata save due to DOM destruction: " + "{}".format(err))

				try:
					await page.wait_for_selector("button, a[role='link'], table", timeout=5000)
					ui_buttons = page.locator("button, a[role='link']")
					count = await ui_buttons.count()
					debug_log(f"{'  ' * depth}🧪 Actionable UI element count: {count}")
					
					page_url = await page.url()
					await crawl_in_page_actions(page, session_id, page_url, ui_buttons)

				except Exception as crawl_err:
					debug_log(f"{'  ' * depth}❌ Sub-panel never loaded or timed out: " + "{}".format(crawl_err))

				await page.go_back()
				await page.wait_for_timeout(1500)
				await expand_hamburger_menu(page, session_id=session_id)

			except Exception as nav_err:
				debug_log(f"{'  ' * depth}❌ Failed nav [{i}]: " + "{}".format(nav_err))
				continue

	except Exception as outer:
		debug_log("❌ Crawl loop error: " + "{}".format(outer))

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

import asyncio
import os
from utils.logging import debug_log
from playwright.async_api import Page, Keyboard
from oracle.ui_mapper.db_inserter import save_ui_page_metadata, insert_ui_element

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

# <<09-JUN-2025:16:28>> - Patched for correct use of insert_ui_element() and defined page_url
 

# <<09-JUN-2025:16:44>> - Accepts 4 arguments and calls insert_ui_element() with full metadata

from utils.logging import debug_log
from oracle.ui_mapper.db_inserter import insert_ui_element

async def crawl_in_page_actions(page, session_id, page_url, elements):
	debug_log("Entered")

	try:
		debug_log(f"🧪 Actionable UI element count: {len(elements)}")
		click_timeout = int(os.getenv("CRAWLER_TIMEOUT", "5000"))

		for i, element in enumerate(elements):
			label = ""
			try:
				label = (await element.inner_text()).strip()
				if not label:
					debug_log(f"  ⏭️ Skipping unnamed element [#{i}]")
					continue

				debug_log(f"  ➡️ {i+1} of {len(elements)} <<{label}>>")

				await element.scroll_into_view_if_needed()
				await element.wait_for(state="visible", timeout=click_timeout)
				await element.click(timeout=click_timeout)

				tag_name = await element.evaluate("el => el.tagName")
				xpath = await element.evaluate("el => window.getXPath(el)")  # Requires helper JS
				css_selector = await element.evaluate("el => el.getAttribute('class') || ''")
				element_type = await element.get_attribute("type") or "unknown"

				# ✅ Save element info to DB
				insert_ui_element({
					"page_url": page_url,
					"label": label,
					"tag_name": tag_name,
					"element_type": element_type,
					"xpath": xpath,
					"css_selector": css_selector,
					"session_id": session_id
				})

			except Exception as e:
				debug_log(f"  ❌ Failed to click sub-action [{i}] ({label}): {str(e)}")

	except Exception as outer:
		debug_log(f"Unhandled in-page crawl error: {str(outer)}")

	debug_log("Exited")

