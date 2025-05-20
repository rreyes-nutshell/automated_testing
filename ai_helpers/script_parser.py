import json
import re
from ai_helpers.llm_utils import run_local_llm, sanitize_llm_json
from utils.logging import debug_log

def parse_script_to_steps(script_text):
	debug_log("Entered")
	prompt = (
		"You are a QA automation expert. Convert the following instruction into valid JSON test steps using Playwright.\n"
		"\n"
		"Instruction:\n"
		f"{script_text}\n"
		"\n"
		"Output JSON using this exact schema:\n"
		"{\n"
		"  \"steps\": [\n"
		"    { \"action\": \"goto\" | \"fill\" | \"click\" | \"wait_for_selector\" | \"assert\", \"selector\": \"...\", \"value\": \"...\", \"target\": \"...\" }\n"
		"  ]\n"
		"}\n"
		"\n"
		"Rules:\n"
		"- Wrap all values in double quotes. No single quotes.\n"
		"- Do not include comments or markdown.\n"
		"- Do not include null values or trailing commas.\n"
		"- Use only: goto, fill, click, wait_for_selector, wait_for_timeout, assert\n"
		"- The entire output must be one valid JSON object starting with { and ending with }.\n"
		"- For login, assume: \"input[name='userid']\", \"input[name='password']\", and button#btnActive\n"
		"- After login, wait for a selector like #pt1\\:pt_h1 or element containing 'Sign Out' to ensure you're fully logged in.\n"
		"- Do NOT use markdown formatting like ```json.\n"
		"\n"
		"Only output valid compact JSON. Do not explain it."
	)

	if "Scheduled Processes" in script_text:
		prompt += (
			"\n"
			"- If navigating to Scheduled Processes, click a[title='Navigator'] then wait for 'Tools', then click it, then click 'Scheduled Processes'.\n"
			"- Use 'wait_for_selector' with 'state=visible' before each click.\n"
			"- You may need to scroll elements into view.\n"
		)

	response = run_local_llm(prompt)
	debug_log("Exited")

	try:
		obj = sanitize_llm_json(response)
		debug_log(f"📦 Parsed steps from LLM: {json.dumps(obj, indent=2)}")
		debug_log("Exited")
		return json.dumps(obj)
	except Exception as e:
		debug_log(f"❌ Failed to parse steps JSON: {e}")
		debug_log(f"🪵 Raw response was: {response}")
		return '{"steps": []}'
