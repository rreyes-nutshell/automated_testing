import asyncio
import os
from playwright.async_api import async_playwright
from oracle.login_steps import run_oracle_login_steps
from oracle.ui_mapper.extractor import extract_nav_metadata
from oracle.ui_mapper.db_writer import DBWriter
from utils.logging import debug_log

stop_flag = False

def cancel_crawl():
	global stop_flag
	stop_flag = True

async def crawl_navigation(login_url, username, password, log_callback):
	global stop_flag
	def safe_log(msg): log_callback(f"🔞 {msg}")

	writer = DBWriter()

        async with async_playwright() as p:
                browser = await p.chromium.launch(headless=os.getenv("HEADLESS", "true").lower() == "true", slow_mo=200)
		page = await browser.new_page()

		safe_log("🌐 Navigating to Oracle login page")
		await run_oracle_login_steps(page, login_url, username, password)

		frames = page.frames
		for f in frames:
			safe_log(f"🔍 Frame: {f.name} — URL: {f.url}")
		target_frame = next((f for f in frames if f.url and "blank.html" not in f.url), page)

		try:
			await target_frame.evaluate("""() => {
				const panel = document.querySelector('div.sca-scrollable');
				if (panel) {
					panel.dispatchEvent(new Event('mouseenter'));
					panel.dispatchEvent(new Event('mouseover'));
					panel.scrollTop = panel.scrollHeight;
				}
			}""")
			safe_log("🌀 Simulated hover + scroll on nav panel")
		except:
			safe_log("⚠️ Could not scroll nav panel")

		await target_frame.wait_for_timeout(7000)

		html = await target_frame.content()
		with open("nav_debug.html", "w", encoding="utf-8") as f:
			f.write(html)
		await page.screenshot(path="nav_debug.png", full_page=True)

		all_links = await target_frame.query_selector_all("a")
		safe_log(f"🧪 Found {len(all_links)} anchor tags")

		for i, link in enumerate(all_links):
			try:
				visible = await link.is_visible()
				if not visible:
					continue
				link_id = await link.get_attribute("id")
				if link_id:
					escaped_id = link_id.replace(":", "\\:")
					selector = f"a#{escaped_id}"
				else:
					continue
				entry = await extract_nav_metadata(target_frame, selector, parent_label="Top")
				if entry:
					await writer.insert_entry(entry)
					safe_log(f"✅ Captured: {entry['label']}")
			except Exception as e:
				safe_log(f"⚠️ Error processing link {i}: {e}")
				continue

		safe_log("🤩 Crawl completed")

def run_with_params(login_url, username, password, log_callback=print):
	global stop_flag
	stop_flag = False

	async def wrapped():
		await crawl_navigation(login_url, username, password, log_callback)

	asyncio.run(wrapped())

if __name__ == "__main__":
	debug_log("⚠️ run_with_params() must be called by web_ui or wrapper.")
