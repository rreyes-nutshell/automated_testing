import json
from utils.logging import debug_log

async def run_steps(page, steps_json):
	debug_log("Entered")
	steps = json.loads(steps_json)["steps"]

	for step in steps:
		action = step.get("action")
		selector = step.get("selector")
		value = step.get("value")
		target = step.get("target")

		try:
			if action == "goto":
				await page.goto(value)
			elif action == "fill":
				await page.fill(selector, value)
			elif action == "click":
				await page.click(selector)
			elif action == "wait_for_selector":
				await page.wait_for_selector(selector)
			elif action == "wait_for_timeout":
				await page.wait_for_timeout(int(value))
			elif action == "assert":
				content = await page.content()
				if value not in content:
					raise Exception(f"Assertion failed: '{value}' not found in page")

			debug_log(f"✅ Step succeeded: {action} - {selector or target}")
		except Exception as e:
			debug_log(f"❌ Step failed: {action} - {selector or target} - {e}")

	debug_log("Exited")
	return await page.content()
