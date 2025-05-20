import json
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from utils.logging import debug_log

class NavigationError(Exception):
	pass

# def load_ui_map(jsonl_path):
# 	debug_log("Entered")
# 	ui_map = {}
# 	try:
# 		with open(jsonl_path, 'r', encoding='utf-8') as f:
# 			for line in f:
# 				try:
# 					item = json.loads(line.strip())
# 					key = (item.get("label"), item.get("parent_label"))
# 					ui_map[key] = item
# 				except Exception as e:
# 					debug_log(f"[load_ui_map] ⚠️ Skipping invalid line: {e}")
# 	except Exception as e:
# 		raise NavigationError(f"Failed to load UI map: {e}")
# 	debug_log("Exited")
# 	return ui_map
def load_ui_map(jsonl_path):
	debug_log("Entered")
	ui_map = {}
	try:
		with open(jsonl_path, 'r', encoding='utf-8') as f:
			for line in f:
				try:
					item = json.loads(line.strip())
					key = (item.get("label"), item.get("parent_label"))
					ui_map[key] = item
				except Exception as e:
					debug_log(f"[load_ui_map] ⚠️ Skipping invalid line: {e}")
	except Exception as e:
		raise NavigationError(f"Failed to load UI map: {e}")
	debug_log("Exited")
	return list(ui_map.values())


def resolve_navigation_path(ui_map, target_page):
        """Return a list of steps leading to the desired page_id."""
        debug_log("Entered")
        path = []
        try:
                current = next((item for item in ui_map if isinstance(item, dict) and item.get("page_id") == target_page), None)
                if not current:
                        raise NavigationError(f"Target page '{target_page}' not found in UI map")
                while current:
                        path.insert(0, current)
                        parent_id = current.get("parent_id")
                        current = next((item for item in ui_map if isinstance(item, dict) and item.get("page_id") == parent_id), None)
        except Exception as e:
                raise NavigationError(f"Failed to resolve path: {e}")
        debug_log("Exited")
        return path

async def execute_navigation(page: Page, navigation_path):
	debug_log("Entered")
	for step in navigation_path:
		action = step.get("action_type")
		selector = step.get("selector")
		value = step.get("value", "")

		try:
			if action == "click":
				await page.click(selector)
			elif action == "fill":
				await page.fill(selector, value)
			elif action == "goto":
				await page.goto(step["url"])
			else:
				raise NavigationError(f"Unsupported action type: {action}")
		except PlaywrightTimeoutError:
			raise NavigationError(f"Timeout executing step: {step}")
		except Exception as e:
			raise NavigationError(f"Failed executing step {step}: {e}")
	debug_log("Exited")

async def navigate_to(page: Page, jsonl_path, target_page):
	debug_log("Entered")
	ui_map = load_ui_map(jsonl_path)
	navigation_path = resolve_navigation_path(ui_map, target_page)
	await execute_navigation(page, navigation_path)
	debug_log("Exited")

def find_page_id_by_label(nav_map, label, parent=None, require_actionable=False):
	debug_log("[find_page_id_by_label] Entered")
	debug_log(f"[find_page_id_by_label] 🔍 Searching for label='{label}' with parent='{parent}' (require_actionable={require_actionable})")
	for entry in nav_map:
		if not isinstance(entry, dict):
			continue
		if entry.get("label") != label:
			continue
		if parent is not None and entry.get("parent") != parent:
			continue
		if require_actionable and not entry.get("is_actionable", False):
			debug_log(f"[find_page_id_by_label] ⛔ Skipping non-actionable: {entry.get('label')}")
			continue
		debug_log(f"[find_page_id_by_label] ✅ Match found: {entry}")
		return entry
	debug_log("[find_page_id_by_label] ❗ No match found for given label/parent")
	return None
