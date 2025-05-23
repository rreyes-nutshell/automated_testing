# oracle/test_executor/executor.py

import asyncio
from playwright.async_api import async_playwright
from utils.logging import debug_log
from oracle.test_executor.runtime_selector import select_click_target
from utils.llm_utils import query_model


async def execute_instruction(page, instruction: str):
	debug_log("Entered")

	# Step 1: Re-scan DOM
	dom_elements = await extract_dom_elements(page)
	if not dom_elements:
		raise RuntimeError("No DOM elements found during scan")

	# Step 2: Let Ollama choose the target selector
	selector = select_click_target(instruction, dom_elements)
	if not selector:
		raise RuntimeError("LLM did not return a valid selector")
	
	# Step 3: Interact with the element
	try:
		await page.click(selector, timeout=5000)
		screenshot_path = f"screenshots/{selector.replace('/', '_').replace(' ', '_')}.png"
		await page.screenshot(path=screenshot_path, full_page=True)
		debug_log(f"Clicked: {selector} and took screenshot -> {screenshot_path}")
	except Exception as e:
		debug_log(f"Failed to click or capture: {e}")
		raise

	debug_log("Exited")


async def extract_dom_elements(page) -> list[str]:
	debug_log("Entered")
	elements = []
	try:
		handles = await page.query_selector_all("*")
		for handle in handles:
			try:
				tag = await handle.get_property("tagName")
				text = await handle.inner_text()
				selector = await page.evaluate("el => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (el.className ? '.' + el.className.replace(/\s+/g, '.') : '')", handle)
				elements.append(f"{selector} - {text.strip()[:100]}")
			except:
				continue
	except Exception as e:
		debug_log(f"DOM extraction failed: {e}")
		return []

	debug_log("Exited")
	return elements


# Sample runner
async def main():
	instruction = "Click any displayed supplier link"
	debug_log("Starting runtime test executor")

	async with async_playwright() as pw:
		browser = await pw.chromium.launch(headless=False)
		context = await browser.new_context()
		page = await context.new_page()
		await page.goto("https://your-oracle-instance-url.com")

		await execute_instruction(page, instruction)

		await browser.close()


if __name__ == "__main__":
	asyncio.run(main())
