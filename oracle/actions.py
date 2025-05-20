# oracle/actions.py

from utils.logging import debug_log

async def wait_and_click(page, selector, timeout=30000):
	debug_log(f"⏳ Waiting for: {selector}")
	await page.wait_for_selector(selector, timeout=timeout)
	await page.click(selector)
	debug_log(f"🖱️ Clicked: {selector}")

async def fill_field(page, selector, value, timeout=30000):
	debug_log(f"⌨️ Filling {selector} with value.")
	await page.wait_for_selector(selector, timeout=timeout)
	await page.fill(selector, value)
	debug_log(f"✅ Filled: {selector}")

async def element_exists(page, selector):
	try:
		await page.wait_for_selector(selector, timeout=2000)
		return True
	except:
		return False
