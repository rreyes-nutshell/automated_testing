import os
import json
import inspect
from datetime import datetime

DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
DEBUG_LEVEL = os.getenv("DEBUG_LEVEL", "normal").lower()

def debug_log(message):
	if DEBUG_MODE:
		# if DEBUG_LEVEL == "v":
		# 	print("DL Set to verbose")
		# else:
		# 	print("DL **NOT** Set to verbose")
		caller = inspect.stack()[1].function
		print(f"🐞 [{caller}] {message}", flush=True)

def is_verbose_debug_enabled():
	return DEBUG_MODE and DEBUG_LEVEL == "v"

def log_step_to_file(step_num, step_data, session_id=None):
	dir_path = f"logs/{session_id}"
	os.makedirs(dir_path, exist_ok=True)

	if is_verbose_debug_enabled():
		timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
		filename = f"step_{str(step_num).replace('.', '_')}_{timestamp}.json"
		filepath = os.path.join(dir_path, filename)
		debug_log("Logging step to file")
		with open(filepath, "w") as f:
			json.dump(step_data, f, indent=2)

async def capture_screenshot(page, session_id, filename, step_num):
	dir_path = f"logs/{session_id}"
	os.makedirs(dir_path, exist_ok=True)
	full_path = os.path.join(dir_path, f"{filename}.png")
	debug_log(f"📸 Saving screenshot: {full_path}")
	try:
		await page.screenshot(path=full_path)
	except Exception as e:
		debug_log(f"❌ Screenshot error: {e}")

async def log_html_to_file(step_num, html, session_id=None):
	dir_path = f"logs/{session_id}"
	os.makedirs(dir_path, exist_ok=True)
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	filename = f"html_{str(step_num).replace('.', '_')}_{timestamp}.html"
	filepath = os.path.join(dir_path, filename)
	with open(filepath, "w", encoding="utf-8") as f:
		f.write(html)
	debug_log(f"📄 HTML snapshot saved: {filepath}")
