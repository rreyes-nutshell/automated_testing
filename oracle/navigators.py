# oracle/navigator_steps.py

from utils.logging import debug_log
from oracle.locators import LOCATORS
from playwright.async_api import Page, TimeoutError as PlaywrightTimeout


async def run_oracle_navigator_steps(page: Page):
	debug_log("🔁 Entered Oracle navigation steps")

	try:
		# Open Navigator menu
		await page.wait_for_selector(LOCATORS["navigation"]["navigator_button"]["selector"], timeout=30000)
		await page.click(LOCATORS["navigation"]["navigator_button"]["selector"])
		debug_log("📂 Navigator opened")
	except PlaywrightTimeout:
		debug_log("❌ Navigator button not found or not clickable")
		return False

	try:
		# Click Tools
		await page.wait_for_selector(f"text={LOCATORS['navigation']['tools_text']['text']}", timeout=30000)
		await page.click(f"text={LOCATORS['navigation']['tools_text']['text']}")
		debug_log("🛠 Tools clicked")
	except PlaywrightTimeout:
		debug_log("❌ Tools text not found or not clickable")
		return False

	try:
		# Click Scheduled Processes
		await page.wait_for_selector(f"text={LOCATORS['navigation']['scheduled_processes_text']['text']}", timeout=30000)
		await page.click(f"text={LOCATORS['navigation']['scheduled_processes_text']['text']}")
		debug_log("📅 Scheduled Processes clicked")
		return True
	except PlaywrightTimeout:
		debug_log("❌ Scheduled Processes text not found or not clickable")
		return False

	debug_log("🏁 Exiting Oracle navigation steps")

