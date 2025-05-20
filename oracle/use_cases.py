from oracle.services import send_to_ollama, run_playwright_action
from utils.logging import debug_log
from openai import OpenAI
import re
import uuid

from services.vector_store import embed_and_store, query_similar
from services.test_case_storage import save_test_case

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

def execute_test_steps(steps, session_id, test_case="Unknown", sheet="Unknown"):
    debug_log("Entered")
    results = []
    for i, step in enumerate(steps):
        context = query_similar(session_id, step, top_k=3)
        prompt = f"""You are an automation assistant. Convert this Oracle test step to a Playwright (Python) action only.
Context:
{chr(10).join(context)}

Step:
{step}
"""
        action = send_to_ollama(prompt)
        embed_and_store(session_id, prompt, action)
        save_test_case(session_id, sheet, test_case, i + 1, action)
        output = run_playwright_action(action)
        results.append((i+1, step, action, output))
    debug_log("Exited")
<<<<<<< HEAD
    return results

def generate_test_cases_by_sheet(sheet_lines_dict):
    debug_log("Entered")
    sheet_results = {}
    total_test_cases = 0
    session_id = str(uuid.uuid4())

    for sheet, lines in sheet_lines_dict.items():
        full_text = "\n".join(lines)
        chunks = [full_text[i:i+3000] for i in range(0, len(full_text), 3000)]
        all_responses = []

        for chunk in chunks:
            prompt = f"""You are an expert QA test script analyzer. Below is a raw export of lines from a sheet named '{sheet}' in an Oracle ERP workbook.
=======
    return results 

def generate_test_cases_by_sheet(sheet_lines_dict):
	debug_log("Entered")
	sheet_results = {}
	total_test_cases = 0
	session_id = str(uuid.uuid4())

	for sheet, blocks in sheet_lines_dict.items():
		debug_log(f"🧾 Processing sheet: {sheet} with {len(blocks)} blocks")

		# Convert list of dicts into raw text chunks for LLM
		full_text = "\n".join(
			f"[{b.get('step_id')}] {b.get('action', '')} → {' | '.join(b.get('steps', []))}"
			for b in blocks
		)

		chunks = [full_text[i:i+3000] for i in range(0, len(full_text), 3000)]
		all_responses = []

		for chunk in chunks:
			prompt = f"""You are an expert QA test script analyzer. Below is a raw export of lines from a sheet named '{sheet}' in an Oracle ERP workbook.
>>>>>>> 61b9b8f (Patch UI Mapper: crawler, extractor, schema updates, HTML fixes)

Your task is to extract and reformat this into clear test steps. Each step should include an action, and optionally an expected result. If you detect multiple test cases, break them apart.

Respond in the following format:

TEST CASE: <Name>
- Step 1: <Action> → <Expected Result>
- Step 2: ...

Here is the raw content:
{chunk}
"""

<<<<<<< HEAD
            response = client.chat.completions.create(
                model="mistral",
                messages=[
                    { "role": "system", "content": "You are an expert QA automation assistant. You convert raw ERP test instructions into structured, step-by-step test cases." },
                    { "role": "user", "content": prompt }
                ],
                temperature=0.2,
            )

            result = response.choices[0].message.content
            embed_and_store(session_id, prompt, result)
            all_responses.append(result)

        combined = "\n\n".join(all_responses)
        case_count = len(re.findall(r'TEST CASE:', combined))
        total_test_cases += case_count
        sheet_results[sheet] = {
            "content": combined,
            "test_case_count": case_count
        }

    debug_log("Exited")
    return sheet_results, total_test_cases
=======
			response = client.chat.completions.create(
				model="mistral",
				messages=[
					{ "role": "system", "content": "You are an expert QA automation assistant. You convert raw ERP test instructions into structured, step-by-step test cases." },
					{ "role": "user", "content": prompt }
				],
				temperature=0.2,
			)

			result = response.choices[0].message.content
			embed_and_store(session_id, prompt, result)
			all_responses.append(result)

		combined = "\n\n".join(all_responses)
		case_count = len(re.findall(r'TEST CASE:', combined))
		total_test_cases += case_count
		sheet_results[sheet] = {
			"content": combined,
			"test_case_count": case_count
		}

	debug_log("Exited")
	return sheet_results, total_test_cases
>>>>>>> 61b9b8f (Patch UI Mapper: crawler, extractor, schema updates, HTML fixes)
