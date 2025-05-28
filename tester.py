# tester.py

import asyncio
import os
from dotenv import load_dotenv
from oracle.test_executor.executor import execute_instruction
from playwright.async_api import async_playwright
from utils.logging import debug_log

# Load environment variables from .env
load_dotenv()

ORA_URL = os.getenv("ORA_URL")
ORA_USER = os.getenv("ORA_USER")
ORA_PW = os.getenv("ORA_PW")

debug_log(f"Loaded ORA_URL: {ORA_URL}")
debug_log(f"Loaded ORA_USER: {ORA_USER}")
debug_log(f"Loaded ORA_PW: {'*' * len(ORA_PW) if ORA_PW else 'None'}")

async def run():
	instruction = "Click any displayed supplier link"
	debug_log("Started tester")

	async with async_playwright() as pw:
		browser = await pw.chromium.launch(headless=False)
		context = await browser.new_context()
		page = await context.new_page()
		await page.goto(ORA_URL)
		await execute_instruction(page, instruction)
		await browser.close()

	debug_log("Completed tester")

if __name__ == "__main__":
	asyncio.run(run())
