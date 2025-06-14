# <<07-JUN-2025:18:45>> - Added load_env to ensure .env values are available before selector_map_file is resolved

import os
import yaml
from utils.logging import debug_log
from utils.env import load_env

load_env()  # <<07-JUN-2025:18:45>> Ensure .env is loaded before os.getenv

SELECTOR_MAP_FILE = os.getenv("SELECTOR_MAP_FILE", "selector_map.yaml")

_selector_cache = None

def load_selector_map():
	debug_log("Entered")
	global _selector_cache
	if _selector_cache is None:
		try:
			with open(SELECTOR_MAP_FILE, 'r') as f:
				_selector_cache = yaml.safe_load(f)
		except Exception as e:
			print(f"⚠️ Failed to load selector map: {e}")
			_selector_cache = {}
	debug_log("Exited")
	return _selector_cache

def get_selector(key_or_selector):
	debug_log("Entered")
	selector_map = load_selector_map()

	# Fallback priority: primary > css > xpath > text > raw
	entry = selector_map.get(key_or_selector)

	if isinstance(entry, str):
		debug_log(f"Resolved selector for '{key_or_selector}': {entry}")
		debug_log("Exited")
		return entry

	elif isinstance(entry, dict):
		primary = entry.get("primary")
		if primary and primary in entry:
			resolved = entry[primary]
			debug_log(f"Resolved selector for '{key_or_selector}': {resolved}")
			debug_log("Exited")
			return resolved
		elif "css" in entry:
			resolved = entry["css"]
			debug_log(f"Resolved selector for '{key_or_selector}': {resolved}")
			debug_log("Exited")
			return resolved
		elif "xpath" in entry:
			resolved = entry["xpath"]
			debug_log(f"Resolved selector for '{key_or_selector}': {resolved}")
			debug_log("Exited")
			return resolved
		elif "text" in entry:
			resolved = f"text='{entry['text']}'"
			debug_log(f"Resolved selector for '{key_or_selector}': {resolved}")
			debug_log("Exited")
			return resolved
		else:
			debug_log(f"⚠️ Key '{key_or_selector}' found in map but structure is unrecognized. Returning raw key.")
			debug_log("Exited")
			return key_or_selector

	# Warn on missing semantic key fallback
	if key_or_selector in selector_map:
		debug_log(f"⚠️ Key '{key_or_selector}' found in map but has invalid structure")
	else:
		debug_log(f"⚠️ Semantic key '{key_or_selector}' not found in selector map. Using as raw string.")

	debug_log("Exited")
	return key_or_selector
