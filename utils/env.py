# <<09-JUN-2025:15:10>> - Enhanced to dynamically print all environment variables

import os
from dotenv import load_dotenv
from utils.logging import debug_log

def load_env():
	debug_log("Entered")
	try:
		env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
		if os.path.exists(env_path):
			load_dotenv(dotenv_path=env_path)
			debug_log(f"Loaded .env from {os.path.abspath(env_path)}")

			# Dynamically print all loaded environment variables
			debug_log("Loaded Environment Variables:")
			for key, value in os.environ.items():
				if key.isupper() and not key.startswith("_"):
					debug_log(f"{key}={value}")
	except Exception as e:
		debug_log(f"load_env error: {e}")
	debug_log("Exited")
