from utils.logging import debug_log
from ai_helpers.llm_utils import run_local_llm, sanitize_llm_json


def parse_instruction_blocks(step_blocks):
	debug_log("Entered")
	parsed_results = []

	for block in step_blocks:
		for step in block.get("steps", []):
			formatted_step_text = "\n".join(
				f"- {line.strip()}" for line in step.get("steps", []) if isinstance(line, str) and line.strip()
			)

			prompt = f"""
You are a synthetic Oracle Cloud staffer automating UI tests. Your job is to read test script instructions and output valid Playwright JSON step definitions.

Instruction Block:
Step ID: {step.get('step_id')}
Action: {step.get('action')}
Steps:
{formatted_step_text}

Expected Result:
{step.get('expected')}

Respond with ONLY a JSON array.
Each object must have: \"action\", \"selector\", and optionally \"value\".
Wrap all keys and string values in double quotes.
Do NOT include markdown, comments, or explanation.
"""

			if '\x00' in prompt or prompt.strip().startswith('<?xml'):
				raise ValueError("❌ Detected invalid or binary prompt input — Excel file may not have been parsed correctly.")

			debug_log(f"🧾 Sending prompt to LLM (first 200 chars): {prompt[:200]}")
			llm_response = run_local_llm(prompt, timeout=block.get("timeout", 30))
			parsed_json = sanitize_llm_json(llm_response)

			# 🛠️ Patch selectors if needed (mirror fallback logic in runner)
			patched_steps = []
			for step_json in parsed_json:
				if not isinstance(step_json, dict):
					debug_log(f"⚠️ Skipping invalid LLM step (not a dict): {step_json}")
					continue

				selector = step_json.get("selector")
				if isinstance(selector, str) and selector.startswith("#") and selector.endswith("-menu"):
					base = selector.lstrip("#").replace("-menu", "").replace("_menu", "").strip()
					if base:
						debug_log(f"🪛 Rewriting selector from '{selector}' to text='{base.capitalize()}'")
						step_json["selector"] = f"text='{base.capitalize()}'"

				patched_steps.append(step_json)

			parsed_results.append({
				"sheet": block["sheet"],
				"step_id": step.get("step_id"),
				"raw": step,
				"llm_json": patched_steps
			})

	debug_log("Exited")
	return parsed_results
