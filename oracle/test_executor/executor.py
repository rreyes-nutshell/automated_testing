import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from oracle.test_executor.runtime_selector import select_click_target, split_instruction
from oracle.login_steps import run_oracle_login_steps
from utils.logging import debug_log
from utils.selectors import escape_css_selector
from oracle.ui_mapper.path_crawler import crawl_path_from_selector

load_dotenv()
ORA_URL = os.getenv("ORA_URL")
ORA_USER = os.getenv("ORA_USER")
ORA_PW = os.getenv("ORA_PW")

debug_log(f"Loaded ORA_URL: {ORA_URL}")
debug_log(f"Loaded ORA_USER: {ORA_USER}")
debug_log(f"Loaded ORA_PW: {'*' * len(ORA_PW) if ORA_PW else 'None'}")


async def find_instruction_target(page, instruction: str) -> tuple[str, str]:
	debug_log("Entered")
	dom_elements = await extract_dom_elements(page)
	if not dom_elements:
		raise RuntimeError("No DOM elements found during scan")

	for el in dom_elements[:10]:
		debug_log(f"🧱 DOM Preview: {el}")
	debug_log(f"🧠 Instruction: {instruction}")
	selector, llm_reasoning, label = select_click_target(instruction, dom_elements)
	debug_log(f"📬 LLM reasoning: {llm_reasoning}")
	debug_log(f"📬 LLM selected: {selector}")
	matched = next((el for el in dom_elements if selector in el), "❓ No DOM match for selector")
	debug_log(f"🧩 Matched element: {matched}")
	if not selector:
		raise RuntimeError("LLM did not return a valid selector")
	debug_log("Exited")
	return selector, matched


async def perform_llm_click(page, selector: str):
	raise NotImplementedError("perform_llm_click is deprecated; use crawl_path_from_selector instead.")


async def extract_dom_elements(page) -> list[str]:
	debug_log("Entered")
	elements = []
	try:
		handles = await page.query_selector_all("*")
		for handle in handles:
			try:
				tag = await handle.get_property("tagName")
				text = await handle.inner_text()
				aria = await handle.get_attribute("aria-label")
				title = await handle.get_attribute("title")
				alt = await handle.get_attribute("alt")
				label = aria or title or alt or text
				selector = await page.evaluate(
					"el => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (el.className ? '.' + el.className.replace(/\\s+/g, '.') : '')",
					handle
				)
				elements.append(f"{selector} - {label.strip()[:100]}")
			except:
				continue
	except Exception as e:
		dbg = f"DOM extraction failed: {e}"
		debug_log(dbg)
		return []

	debug_log("Exited")
	return elements


async def main():
	high_level_instruction = """
You are an Oracle Cloud QA Tester. First, click the 'Suppliers' link. After the Suppliers page loads, locate the first visible supplier name in any data grid and click it. Once the supplier detail screen appears, take a full-page screenshot and save it as 'supp.png' in the root directory.
"""
	debug_log("Starting LLM-driven test chain")

	async with async_playwright() as pw:
		browser = await pw.chromium.launch(headless=False)
		context = await browser.new_context()
		page = await context.new_page()

		navigated_label = None
		breadcrumbs = []

		# 🔐 Login once per test case
		await run_oracle_login_steps(page, ORA_URL, ORA_USER, ORA_PW)
		await page.wait_for_timeout(3000)

		dom_elements = await extract_dom_elements(page)
		visible_labels = sorted(set(el.split(' - ')[-1].strip() for el in dom_elements if ' - ' in el))
		parsed_steps = split_instruction(high_level_instruction.strip(), visible_labels)

		for idx, instruction in enumerate(parsed_steps):
			if any(skip in instruction.lower() for skip in ["login", "log in", "hamburger", "menu icon", "test management", "run test case", "submit", "record the results", "log out"]):
				debug_log(f"⏭️ Skipping redundant step {idx+1}: {instruction}")
				continue

			debug_log(f"🔁 Step {idx+1}: {instruction}")
			label = None
			selector = None

			if any(kw in instruction.lower() for kw in ["click", "select", "choose"]):
				dom_elements = await extract_dom_elements(page)
				selector, matched, label = select_click_target(instruction, dom_elements)
				debug_log(f"🔁 Using selector as-is: {selector}")
				label = matched.split(" - ")[-1].strip().strip("'").strip('"')
				await crawl_path_from_selector(
					page=page,
					label=label,
					selector=selector,
					username=ORA_USER,
					password=ORA_PW,
					login_url=ORA_URL,
					crawler_name="llm_executor",
					session_id="llm_test_session",
					already_logged_in=True  # ✅ ensures login is NOT re-run
				)
			elif "screenshot" in instruction.lower():
				await page.screenshot(path="supp.png", full_page=True)
				debug_log("📸 Saved screenshot to supp.png")
			else:
				debug_log("⚠️ No selector to click and no recognized instruction action.")

			if label:
				breadcrumbs.append(label)

		with open("breadcrumb_trail.txt", "w") as f:
			f.write(" > ".join(breadcrumbs))
		debug_log("📄 Saved breadcrumb trail to breadcrumb_trail.txt")

		await browser.close()


if __name__ == "__main__":
	asyncio.run(main())
