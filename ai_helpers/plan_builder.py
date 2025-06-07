# ai_helpers/plan_builder.py

from typing import List, Dict
import json
from utils.logging import debug_log
from ai_helpers.llm_utils import run_local_llm, sanitize_llm_json  # Use Ollama via CLI instead of openai

async def llm_build_plan(test_instructions: List[str], html_snapshot: str) -> List[Dict]:
	"""
	<<01-JUN-2025:12:55>> - Updated to use run_local_llm (Ollama CLI) instead of openai client
	"""
	debug_log("Entered")

	# Combine instructions into a numbered list
	instructions_text = "\n".join(f"{idx + 1}. {step}" for idx, step in enumerate(test_instructions))

	# Build prompt
	system_message = (
		"You are an AI that converts a list of test instructions and an HTML snapshot "
		"into a JSON array of Playwright steps. Each step object must have keys: "
		"action, selector, and (optionally) value."
	)
	# user_message = (
	# 	"You are already logged in. Do NOT include any steps that navigate back to the login page or fill in username/password.\n"
	# 	"Only produce steps starting from the authenticated home page in the form of a JSON array, for example:\n"
	# 	"[\n"
	# 	"  { \"action\": \"click\", \"selector\": \"<CSS or text selector>\", \"value\": null },\n"
	# 	"  { \"action\": \"wait_for_selector\", \"selector\": \"<CSS or text selector>\", \"value\": null },\n"
	# 	"  { \"action\": \"fill\", \"selector\": \"<CSS selector>\", \"value\": \"<text>\" }\n"
	# 	"]\n\n"
	# 	f"Test Instructions:\n{instructions_text}\n\n"
	# 	f"Initial Page HTML:\n\"\"\"{html_snapshot}\"\"\"\n\n"
	# 	"Respond *only* with a JSON array of objects—no extra text, comments, or login steps."
# ai_helpers/plan_builder.py

# … inside llm_build_plan(), replace the existing user_message with:

	

	user_message = (
	"You are an AI assistant that must return a JSON array …\n"
	"Here are the test instructions:\n"
	"Return only the JSON array, without code fences or text.\n"
	f"{instructions_text}\n\n"
	"Here is the HTML snapshot:\n"
	f"{html_snapshot}\n\n"
	"Example output (exactly as shown, no extra formatting,do not add any trailing comments):\n"
	'[\n'
	'  {\n'
	'    "test_name": "Some Random Test 1",\n'
	'    "steps": [\n'
	'      { "action": "click", "selector": "text=<<value>>" },\n'
	'      { "action": "click", "selector": "text=<<value>> },\n'
	'      { "action": "click", "selector": "css=<<value>>" },\n'
	'      { "action": "click", "selector": "css=<<value>>" }\n'
	'    ]\n'
	'  },\n'
	'  {\n'
	'    "test_name": "Some Random Test 2",\n'
	'    "steps": [\n'
	'      { "action": "click", "selector": "text=<value>>" },\n'
	'      { "action": "click", "selector": "text=<value>>" },\n'
	'      { "action": "click", "selector": "css=<value>>" },\n'
	'      { "action": "click", "selector": "css=<value>>" }\n'
	'    ]\n'
	'  }\n'
	']'
	)

	# Construct full prompt string
	full_prompt = f"{system_message}\n\n{user_message}"
	debug_log(f"[llm_build_plan] Full prompt: {full_prompt}")
	# Call Ollama via CLI
	raw = run_local_llm(full_prompt)
	if not raw:
		debug_log("[llm_build_plan] ⚠️ No output from run_local_llm")
		debug_log("Exited")
		return []

	# Sanitize JSON
	steps_data = sanitize_llm_json(raw)
	debug_log(f"[llm_build_plan] Sanitized JSON: {steps_data}")
	plan = steps_data if isinstance(steps_data, list) else steps_data.get("steps", [])

	debug_log("Exited")
	return plan
