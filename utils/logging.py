# <<07-JUN-2025:18:50>> - Dynamic env loading for debug mode and level

import sys
import os
import json
import inspect
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

# Internal state flags
_DEBUG_MODE = False
_DEBUG_LEVEL = "normal"

def get_debug_flags():
	global _DEBUG_MODE, _DEBUG_LEVEL
	_DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
	_DEBUG_LEVEL = os.getenv("DEBUG_LEVEL", "normal").lower()
	return _DEBUG_MODE, _DEBUG_LEVEL

def debug_log(message):
	mode, _ = get_debug_flags()
	if mode:
		frame = inspect.stack()[1]
		filename = os.path.basename(frame.filename)
		function_name = frame.function
		caller = f"{filename}:{function_name}"
		print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 🐞 [{caller}] {message}", flush=True, file=sys.stderr)

def is_verbose_debug_enabled():
	mode, level = get_debug_flags()
	return mode and level == "v"

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

# ----------------------------------------------------------------------------
# Environment helpers
# ----------------------------------------------------------------------------

def load_env() -> bool:
	"""Load environment variables using dotenv and recompute debug flags."""
	dotenv_path = find_dotenv(usecwd=True)
	if dotenv_path:
		load_dotenv(dotenv_path, override=False)
		debug_log(f"Loaded .env from {dotenv_path}")
	else:
		debug_log("No .env file found via find_dotenv; relying on process envs")

	get_debug_flags()  # Refresh DEBUG_MODE/DEBUG_LEVEL

	return os.getenv("HEADLESS_MODE", "true").lower() == "true"
