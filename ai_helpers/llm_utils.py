# # /ai_helpers/llm_utils.py
# import os
# import re
# import requests
# import json
# from utils.logging import debug_log
# from typing import List, Dict
# import openai  # or your local‐LLM client

# OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
# OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")  # Or "command-r" etc.


# def run_local_llm(prompt: str, timeout: int = 60) -> str:
#     debug_log("Entered")
#     debug_log(f"📝 LLM prompt (length: {len(prompt)}): {prompt}")
#     debug_log(f"📝 OLLAMA_HOST : {OLLAMA_HOST}")
#     try:
#         response = requests.post(
#             f"{OLLAMA_HOST}/api/generate",
#             json={
#                 "model": OLLAMA_MODEL,
#                 "prompt": prompt,
#                 "stream": False
#             },
#             timeout=timeout
#         )
#         response.raise_for_status()
#         content = response.json()
#         result = content.get("response", "").strip()
#         debug_log(f"🧮 Token stats — input: {content.get('prompt_eval_count')}, output: {content.get('eval_count')}")
#         debug_log("Exited")
#         return result
#     except requests.exceptions.Timeout as e:
#         debug_log(f"🛑 LLM request timed out: {e}")
#         return "ERROR_TIMEOUT"
#     except Exception as e:
#         debug_log(f"❌ LLM call failed: {e}")
#         return f"ERROR: {e}"


# def sanitize_llm_json(raw: str) -> dict:
#     debug_log("Entered")
#     if "import React" in raw or "export default" in raw:
#         debug_log("❌ Rejected LLM response due to React/JS component content")
#         return []
#     raw = raw.strip()
#     raw = "\n".join(line for line in raw.splitlines() if not line.strip().startswith("//"))
#     raw = re.sub(r"^```(?:json)?", "", raw, flags=re.IGNORECASE).strip()
#     raw = re.sub(r"```$", "", raw)

#     array_start = raw.find('[')
#     object_start = raw.find('{')

#     if array_start != -1 and (object_start == -1 or array_start < object_start):
#         start = array_start
#         end = raw.rfind(']') + 1
#     else:
#         start = object_start
#         end = raw.rfind('}') + 1

#     if start == -1 or end == -1:
#         debug_log("⚠️ Falling back to safe_extract_json due to missing JSON bounds")
#         return safe_extract_json(raw)

#     json_fragment = raw[start:end]

#     json_fragment = re.sub(r",\s*([}\]])", r"\1", json_fragment)
#     json_fragment = re.sub(r'(?<={|,)(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_fragment)
#     json_fragment = json_fragment.replace("\\\"", '"')
#     json_fragment = re.sub(r'"\s*\'(.*?)\'\s*"', r'"\1"', json_fragment)
#     json_fragment = re.sub(r"'\s*\"(.*?)\"\s*'", r'"\1"', json_fragment)
#     json_fragment = re.sub(r":\s*'([^']*?)'", r': "\1"', json_fragment)
#     json_fragment = re.sub(r"'([^']*?)'", r'\1', json_fragment)
#     json_fragment = json_fragment.replace("'", '"')

#     json_fragment = re.sub(
#         r'"selector"\s*:\s*"([^"]*?)"',
#         lambda m: '"selector": "' + m.group(1).replace('"', '') + '"',
#         json_fragment
#     )

#     json_fragment = re.sub(
#         '"selector"\s*:\s*"get_by_role\\(\\"(\\w+)\\", name=\\"([^)]+)\\"\\)"',
#         lambda m: f'"action": "click_by_role", "role": "{m.group(1)}", "name": "{m.group(2)}"',
#         json_fragment
#     )

#     json_fragment = re.sub(r'"[^"\n]*$', '', json_fragment)

#     try:
#         result = json.loads(json_fragment)
#     except json.JSONDecodeError as e:
#         debug_log(f"⚠️ JSON decode failed after normalization: {e}")
#         debug_log("⚠️ Falling back to safe_extract_json")
#         result = safe_extract_json(raw)

#     debug_log("Exited")
#     return result


# def safe_extract_json(response_text):
#     debug_log("Entered safe_extract_json")
#     match = re.search(r'(\[.*?\]|\{.*?\})', response_text, re.DOTALL)
#     if not match:
#         debug_log("❌ No JSON detected in LLM response")
#         return []

#     json_fragment = match.group(1)
#     try:
#         parsed = json.loads(json_fragment)
#     except json.JSONDecodeError as e:
#         debug_log(f"❌ JSON decode error in safe_extract_json: {e}")
#         parsed = []

#     debug_log("Exited safe_extract_json")
#     return parsed

# # <<01-JUN-2025:10:00>> - Added llm_build_plan helper

# async def llm_build_plan(test_instructions: List[str], html_snapshot: str) -> List[Dict]:
# 	debug_log("Entered")
# 	# Combine instructions into a numbered list
# 	instructions_text = "\n".join(f"{idx + 1}. {step}" for idx, step in enumerate(test_instructions))

# 	# Build system and user messages
# 	system_message = (
# 		"You are an AI that converts a list of test instructions and an HTML snapshot "
# 		"into a JSON array of Playwright steps. Each step object must have keys: "
# 		"action, selector, and (optionally) value."
# 	)
# 	user_message = (
# 		f"Test Instructions:\n{instructions_text}\n\n"
# 		f"Initial Page HTML:\n\"\"\"{html_snapshot}\"\"\"\n\n"
# 		"Respond *only* with a JSON array of objects, "
# 		"for example:\n"
# 		"[\n"
# 		"  {\"action\": \"goto\", \"selector\": \"https://app.example.com/login\", \"value\": null},\n"
# 		"  {\"action\": \"fill\", \"selector\": \"#username\", \"value\": \"user1\"},\n"
# 		"  {\"action\": \"fill\", \"selector\": \"#password\", \"value\": \"pass123\"},\n"
# 		"  {\"action\": \"click\", \"selector\": \"button[type=submit]\", \"value\": null}\n"
# 		"]"
# 	)

# 	# Use the async ChatCompletion API in openai>=1.0.0
# 	try:
# 		response = await openai.ChatCompletion.acreate(
# 			model="local-llm",
# 			messages=[
# 				{"role": "system", "content": system_message},
# 				{"role": "user",   "content": user_message}
# 			]
# 		)
# 	except Exception as e:
# 		debug_log(f"[llm_build_plan] ❌ OpenAI API error: {e}")
# 		debug_log("Exited")
# 		return []

# 	content = response.choices[0].message.content
# 	try:
# 		plan = json.loads(content)
# 	except Exception as e:
# 		debug_log(f"[llm_build_plan] ❌ Failed to parse JSON from LLM response: {e}")
# 		debug_log(f"[llm_build_plan] 💕 Raw response was: {content}")
# 		plan = []
	
# 	debug_log("Exited")
# 	return plan
# ai_helpers/llm_utils.py

# ai_helpers/llm_utils.py
##
## 6/1 pre change version above.  below we are implementing LLM multi step plan generation
##
# ai_helpers/llm_utils.py

# ai_helpers/llm_utils.py
# ai_helpers/llm_utils.py
# ai_helpers/llm_utils.py
# ai_helpers/llm_utils.py

# ai_helpers/llm_utils.py
# ai_helpers/llm_utils.py
import os
from typing import List, Dict, Any
import json
import re
from utils.logging import debug_log
import subprocess
import shlex

# def run_local_llm(prompt: str, timeout: int = 30) -> str:
#     """
#     <<01-JUN-2025:12:55>> - Synchronously invoke a local LLM process (Ollama) to generate a raw text response.
#     Automatically pull the Mistral model if not present, then retry.
#     """
#     debug_log("Entered")
#     model_name = "mistral"
#     def invoke():
#         cmd = f"ollama run {model_name} {shlex.quote(prompt)}"
#         return subprocess.run(
#             shlex.split(cmd),
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#             timeout=timeout
#         )

#     try:
#         result = invoke()
#         if result.returncode != 0:
#             stderr = result.stderr.strip()
#             if "pull model manifest" in stderr.lower() or "model not found" in stderr.lower():
#                 debug_log(f"[run_local_llm] Model '{model_name}' not found locally. Pulling model...")
#                 pull_cmd = f"ollama pull {model_name}"
#                 pull_result = subprocess.run(
#                     shlex.split(pull_cmd),
#                     stdout=subprocess.PIPE,
#                     stderr=subprocess.PIPE,
#                     text=True,
#                     timeout=timeout
#                 )
#                 if pull_result.returncode != 0:
#                     debug_log(f"[run_local_llm] ❌ Failed to pull model '{model_name}': {pull_result.stderr.strip()}")
#                     return ""
#                 result = invoke()
#                 if result.returncode != 0:
#                     debug_log(f"[run_local_llm] ❌ LLM process error after pull: {result.stderr.strip()}")
#                     return ""
#             else:
#                 debug_log(f"[run_local_llm] ❌ LLM process error: {stderr}")
#                 return ""
#         raw_output = result.stdout.strip()

#     except subprocess.TimeoutExpired:
#         debug_log(f"[run_local_llm] ❌ Ollama CLI timed out after {timeout} seconds")
#         raw_output = ""
#     except Exception as e:
#         debug_log(f"[run_local_llm] ❌ Exception when invoking LLM: {e}")
#         raw_output = ""
#     debug_log("Exited")
#     return raw_output


from typing import Dict
import requests
from utils.logging import debug_log
from utils.env import load_env

def run_remote_llm(prompt: str, timeout: int = 30) -> str:
	"""
	<<10-JUN-2025:16:40>> - Calls remote Ollama instance over HTTP and returns the generated response.
	"""
	debug_log("Entered")
	load_env()  # Ensure environment variables are loaded
	OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
	OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")  # Or "command-r" etc.

	url = f"{OLLAMA_HOST}/api/generate"
	payload = { 
		"model": OLLAMA_MODEL,
		"prompt": prompt,
		"stream": False  # set to True if you want token streaming (requires different handling)
	}

	try:
		response = requests.post(url, json=payload, timeout=timeout)
		response.raise_for_status()
		output = response.json().get("response", "").strip()
	except requests.exceptions.RequestException as e:
		debug_log(f"[run_remote_llm] ❌ Request error: {e}")
		output = ""
	except Exception as e:
		debug_log(f"[run_remote_llm] ❌ Unexpected error: {e}")
		output = ""

	debug_log("Exited")
	return output



# def sanitize_llm_json(raw: str) -> list:
#     """
#     <<01-JUN-2025:12:25>> - Attempt to coerce the LLM’s output into valid JSON.
#     Handles common formatting issues: code fences, extra text, single vs. double quotes,
#     trailing commas, nested comments, and malformed or empty selectors (including XPath).
#     Returns a list of well-formed step dicts (action, selector, value).
#     """
#     debug_log("Entered")
#     cleaned = raw

#     # 1. Remove Markdown code fences ```json ... ``` if present
#     code_fence_pattern = r"```(?:json)?(.*?)```"
#     matches = re.findall(code_fence_pattern, cleaned, flags=re.DOTALL)
#     if matches:
#         cleaned = matches[0].strip()
#         debug_log("[sanitize_llm_json] Stripped Markdown code fences")

#     # 2. Extract JSON-looking substring between balanced braces/brackets
#     def extract_json_substring(text: str) -> str:
#         stack = []
#         start_index = None
#         for i, ch in enumerate(text):
#             if ch == '{' or ch == '[':
#                 if start_index is None:
#                     start_index = i
#                 stack.append(ch)
#             elif ch == '}' or ch == ']':
#                 if stack:
#                     stack.pop()
#                     if not stack and start_index is not None:
#                         return text[start_index:i+1]
#         return text

#     extracted = extract_json_substring(cleaned)
#     if extracted != cleaned:
#         cleaned = extracted
#         debug_log("[sanitize_llm_json] Extracted JSON-like substring")

#     # 2.5 Strip out JavaScript-style comments
#     cleaned = re.sub(r"//.*?$", "", cleaned, flags=re.MULTILINE)    # Remove single-line // comments
#     cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)    # Remove multi-line /* ... */ comments

#     # 3. Normalize quotation marks: replace single quotes with double quotes when safe
#     cleaned = re.sub(r"'(?=[^,{}[\]]*?:)", '"', cleaned)  # quotes before colon (keys)
#     cleaned = re.sub(r"(?<=: )'(.*?)(?=')", r'"\1"', cleaned)  # quotes around values
#     cleaned = cleaned.replace("’", "\"").replace("“", "\"").replace("”", "\"")

#     # 4. Remove trailing commas before closing braces/brackets
#     cleaned = re.sub(r",\s*}", "}", cleaned)
#     cleaned = re.sub(r",\s*]", "]", cleaned)

#     # 5. Remove any non-ASCII control characters
#     cleaned = re.sub(r"[\x00-\x1F\x7F]", "", cleaned)

#     # 6. Attempt to extract individual JSON objects from the array-like text
#     #    by matching every substring that looks like { ... }
#     object_pattern = r"\{[^}]*\}"
#     step_objects = re.findall(object_pattern, cleaned, flags=re.DOTALL)

#     filtered_steps = []
#     for obj_text in step_objects:
#         try:
#             step = json.loads(obj_text)
#         except Exception:
#             continue

#         # Validate the step dict
#         action   = step.get("action")
#         selector = (step.get("selector") or "").strip()
#         value    = step.get("value", None)

#         # Only allow known actions
#         if action not in {"click", "fill", "goto", "wait_for_selector", "downloadFile", "saveAsFile"}:
#             continue

#         # Drop any selector that is empty or begins with 'xpath:'
#         if not selector or selector.lower().startswith("xpath:"):
#             continue

#         # At this point, we trust selector is either 'text=…' or a valid CSS selector
#         filtered_steps.append({
#             "action":   action,
#             "selector": selector,
#             "value":    value
#         })

#     debug_log("Exited")
#     return filtered_steps
# <<01-JUN-2025:23:00>> - Modified sanitize_llm_json to accept a top-level array of test-case objects

# def sanitize_llm_json(raw_output: str) -> List[Dict[str, Any]]:
# 	# [Original implementation commented out below]
# 	# 🐞 [sanitize_llm_json] Stripped Markdown code fences
# 	# 🐞 [sanitize_llm_json] Extracted JSON-like substring
# 	# ... (remaining original code) ...
# 	# return filtered_steps

def sanitize_llm_json(raw_output: str) -> List[Dict[str, Any]]:
	"""
	Attempt to parse the entire LLM output as a top-level JSON array of test-case objects.
	If that fails, fall back to extracting individual step objects via regex as before.
	"""
	from typing import Any, Dict, List
	import json
	import re

	debug_log("🐞 [sanitize_llm_json] Entered, attempting to parse entire JSON array")

	# 1. Try to parse the raw_output directly as JSON.
	try:
		parsed = json.loads(raw_output)
		debug_log(f"🚩 Raw LLM output:\n{raw_output!r}")
		# If it's a list of dicts, assume it's our array of test-case objects.
		if isinstance(parsed, list) and all(isinstance(obj, dict) for obj in parsed):
			debug_log("🐞 [sanitize_llm_json] Successfully parsed top-level JSON array"	)
			return parsed  # return array of test-case objects
	except Exception as e:
		debug_log(f"🐞 [sanitize_llm_json] Failed top-level JSON parse: {e}")

	# 2. Fallback: use old regex-based extraction of individual step objects
	debug_log("[sanitize_llm_json] Falling back to step-wise extraction")

	# Extract every {...} chunk
	braced_chunks = re.findall(r"\{[^}]*\}", raw_output, re.DOTALL)
	valid_steps: List[Dict[str, Any]] = []

	for chunk in braced_chunks:
		try:
			obj = json.loads(chunk)
		except json.JSONDecodeError:
			continue

		selector = obj.get("selector", "")
		# Only keep objects with a non-empty selector in text= or css= form
		if isinstance(selector, str) and (selector.startswith("text=") or selector.startswith("css=")):
			valid_steps.append(obj)

	debug_log(f"🐞 [sanitize_llm_json] Extracted {len(valid_steps)} valid step objects")
	return valid_steps
