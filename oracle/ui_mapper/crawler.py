from utils.logging import debug_log
from utils.db_utils import get_db_connection
from oracle.login_steps import run_oracle_login_steps
from oracle.ui_mapper.extractor import extract_nav_metadata
from oracle.ui_mapper.db_writer import DBWriter
from playwright.async_api import async_playwright
from dotenv import load_dotenv, find_dotenv
import asyncio
import os
from datetime import datetime
import uuid
import json

async def crawl_oracle_ui(username, password, crawler_name="default", session_id=None, login_url=None):

	debug_log("Entered")

	# Load variables from .env file (optional: specify the path)
	env_path = find_dotenv()
	print(f"Found .env at: {env_path}")

	load_dotenv(env_path)

	# Print all loaded environment variables
	for key, value in os.environ.items():
		debug_log(f'{key}={value}')
	
	if session_id is None:
		session_id = str(uuid.uuid4())

	writer = DBWriter("oracle_ui_dump.jsonl")
	extracted = []
	headless_mode = os.getenv("HEADLESS", "true").lower() == "true"

	debug_log(f"🧙️ Headless Mode: {headless_mode}")
	headless_mode = False  # For debugging purposes
	async with async_playwright() as p:
		browser = await p.chromium.launch(
			headless=headless_mode
		)
		context = await browser.new_context()
		page = await context.new_page()
		username = "mgonzalez@mfa.org"
		password = "Welcome!23"
		login_url = "https://login-ibnijb-dev1.fa.ocs.oraclecloud.com"
		await run_oracle_login_steps(page, login_url, username, password)
		debug_log("Logged in")

		is_superuser = os.getenv("IS_SUPERUSER", "false").lower() == "true"
		await extract_nav_metadata(page, username, is_superuser, session_note=session_id)

		# Skip database query, manually mock links or pull from page
		# Example placeholder
		nav_links = [
			("Home", "a#pt1\:_UISnvr\:0\:nv_itemNode_home"),
			("Suppliers", "a#pt1\:_UISnvr\:0\:nv_itemNode_procurement_suppliers")
		]

		for i, row in enumerate(nav_links):
			try:
				label, selector = row
				element = page.locator(selector)
				await element.wait_for(state="attached", timeout=5000)
				await element.click()
				await asyncio.sleep(1)
				extracted.append({"label": label, "selector": selector})
				debug_log(f"✅ Clicked {label}")
			except Exception as e:
				debug_log(f"⚠️ Error processing link {i}: {e}")

		await browser.close()

		# Save to JSON file instead of DB
		output_path = f"click_results_{session_id}.json"
		with open(output_path, "w") as f:
			json.dump({"session_id": session_id, "results": extracted}, f, indent=2)

		debug_log(f"📝 Saved results to {output_path}")

		# Export full UI map to logs directory
		from oracle.ui_mapper.exporter import export_db_to_jsonl
		log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs'))
		os.makedirs(log_dir, exist_ok=True)
		export_path = os.path.join(log_dir, f"ui_map_{session_id}.jsonl")
		export_db_to_jsonl(export_path, get_db_connection())
		debug_log(f"📝 UI map exported to {export_path}")

	debug_log("Exited")

if __name__ == "__main__":
	asyncio.run(crawl_oracle_ui("your_user", "your_pass"))
