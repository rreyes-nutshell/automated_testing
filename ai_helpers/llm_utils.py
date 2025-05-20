<<<<<<< HEAD
=======
# /ai_helpers/llm_utils.py

>>>>>>> 61b9b8f (Patch UI Mapper: crawler, extractor, schema updates, HTML fixes)
import os
import re
import requests
import json
from utils.logging import debug_log

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")  # Or "command-r" etc.

<<<<<<< HEAD
def run_local_llm(prompt: str) -> str:
	debug_log("Entered")
	try:
		response = requests.post(
			f"{OLLAMA_HOST}/api/generate",
=======
def run_local_llm(prompt: str, timeout: int = 30) -> str:
	debug_log("Entered")

	debug_log(f"📝 LLM prompt (length: {len(prompt)}): {prompt}")

	debug_log(f"📝 OLLAMA_HOST ( : {OLLAMA_HOST}")
	try:
		response = requests.post(
			f"{OLLAMA_HOST}/api/generate",			
			# "http://localhost:11434/api/generate",
>>>>>>> 61b9b8f (Patch UI Mapper: crawler, extractor, schema updates, HTML fixes)
			json={
				"model": OLLAMA_MODEL,
				"prompt": prompt,
				"stream": False
			},
<<<<<<< HEAD
			timeout=30
=======
			timeout=timeout
>>>>>>> 61b9b8f (Patch UI Mapper: crawler, extractor, schema updates, HTML fixes)
		)
		response.raise_for_status()
		content = response.json()
		result = content.get("response", "").strip()
<<<<<<< HEAD
		debug_log("Exited")
		return result
=======
		debug_log(f"🧮 Token stats — input: {content.get('prompt_eval_count')}, output: {content.get('eval_count')}")
		debug_log("Exited")
		return result
	except requests.exceptions.Timeout as e:
		debug_log(f"🛑 LLM request timed out: {e}")
		return "ERROR_TIMEOUT"

>>>>>>> 61b9b8f (Patch UI Mapper: crawler, extractor, schema updates, HTML fixes)
	except Exception as e:
		debug_log(f"❌ LLM call failed: {e}")
		return f"ERROR: {e}"

<<<<<<< HEAD
def sanitize_llm_json(raw: str) -> dict:
=======

def sanitize_llm_json(raw: str) -> dict:
	# Quick rejection if response is obviously code
	if "import React" in raw or "export default" in raw:
		debug_log("❌ Rejected LLM response due to React/JS component content")
		return []
>>>>>>> 61b9b8f (Patch UI Mapper: crawler, extractor, schema updates, HTML fixes)
	raw = raw.strip()
	raw = "\n".join(line for line in raw.splitlines() if not line.strip().startswith("//"))
	raw = re.sub(r"^```(?:json)?", "", raw, flags=re.IGNORECASE).strip()
	raw = re.sub(r"```$", "", raw)

<<<<<<< HEAD
	# Try to extract the first full JSON block
	start = raw.find('{')
	end = raw.rfind('}') + 1
	if start == -1 or end == -1:
		raise ValueError("No valid JSON object found in response")
=======
	# === PATCH: Support array-level JSON, not just object-level JSON ===
	array_start = raw.find('[')
	object_start = raw.find('{')

	if array_start != -1 and (object_start == -1 or array_start < object_start):
		start = array_start
		end = raw.rfind(']') + 1
	else:
		start = object_start
		end = raw.rfind('}') + 1

	if start == -1 or end == -1:
		debug_log("⚠️ Falling back to safe_extract_json due to missing JSON bounds")
		return safe_extract_json(raw)
	# === END PATCH ===

>>>>>>> 61b9b8f (Patch UI Mapper: crawler, extractor, schema updates, HTML fixes)
	json_fragment = raw[start:end]

	# Clean trailing commas
	json_fragment = re.sub(r",\s*([}\]])", r"\1", json_fragment)

	# Quote unquoted keys
	json_fragment = re.sub(r'(?<={|,)(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_fragment)

	# Clean malformed/escaped quotes from LLM
	json_fragment = json_fragment.replace("\\\"", '"')
	json_fragment = re.sub(r'"\s*\'(.*?)\'\s*"', r'"\1"', json_fragment)
	json_fragment = re.sub(r"'\s*\"(.*?)\"\s*'", r'"\1"', json_fragment)
	json_fragment = re.sub(r":\s*'([^']*?)'", r': "\1"', json_fragment)
	json_fragment = re.sub(r"'([^']*?)'", r'\1', json_fragment)
	json_fragment = json_fragment.replace("'", '"')

	# Last pass: ensure consistent double quotes in selectors
<<<<<<< HEAD
	json_fragment = re.sub(r'"selector"\s*:\s*"([^\"]*?)"', lambda m: f'"selector": "{m.group(1).replace("\"", "")}"', json_fragment)

	# Replace get_by_role with click_by_role
	json_fragment = re.sub(
		'"selector"\s*:\s*"get_by_role\\(\\\"(\w+)\\\", name=\\\"([^)]+)\\\"\\)"',
=======
	json_fragment = re.sub(
		r'"selector"\s*:\s*"([^"]*?)"',
		lambda m: '"selector": "' + m.group(1).replace('"', '') + '"',
		json_fragment
	)


	# Replace get_by_role with click_by_role
	json_fragment = re.sub(
		'"selector"\s*:\s*"get_by_role\\(\\\"(\\w+)\\\", name=\\\"([^)]+)\\\"\\)"',
>>>>>>> 61b9b8f (Patch UI Mapper: crawler, extractor, schema updates, HTML fixes)
		lambda m: f'"action": "click_by_role", "role": "{m.group(1)}", "name": "{m.group(2)}"',
		json_fragment
	)

<<<<<<< HEAD
	if not json_fragment.startswith("{") or not json_fragment.endswith("}"):
		raise ValueError("Sanitized JSON fragment is not valid JSON")

	return json.loads(json_fragment)
=======
	# === PATCH: Remove unterminated trailing strings that break parsing ===
	json_fragment = re.sub(r'"[^"\n]*$', '', json_fragment)
	# === END PATCH ===

	try:
		return json.loads(json_fragment)
	except json.JSONDecodeError as e:
		debug_log(f"⚠️ JSON decode failed after normalization: {e}")
		debug_log("⚠️ Falling back to safe_extract_json")
		return safe_extract_json(raw)


def safe_extract_json(response_text):
	"""
	Extracts the first valid JSON object or array from possibly messy LLM output.
	Use this instead of sanitize_llm_json when output may be polluted.
	"""
	debug_log("Entered safe_extract_json")
	match = re.search(r'(\[.*?\]|\{.*?\})', response_text, re.DOTALL)
	if not match:
		debug_log("❌ No JSON detected in LLM response")
		return []

	json_fragment = match.group(1)
	try:
		parsed = json.loads(json_fragment)
	except json.JSONDecodeError as e:
		debug_log(f"❌ JSON decode error in safe_extract_json: {e}")
		parsed = []

	debug_log("Exited safe_extract_json")
	return parsed
>>>>>>> 61b9b8f (Patch UI Mapper: crawler, extractor, schema updates, HTML fixes)
