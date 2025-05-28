from utils.logging import debug_log
from ai_helpers.llm_utils import run_local_llm  # ✅ fixed
from difflib import SequenceMatcher

def select_click_target(instruction: str, dom_elements: list[str]) -> tuple[str, str, str]:
	debug_log("Entered")

	if not instruction or not dom_elements:
		raise ValueError("Instruction and DOM elements must be provided")

	def is_interactive(label: str, selector: str) -> bool:
		non_actions = ["script", "style", "link", "meta", "img", "iframe", "form", "noscript"]
		interactive_prefixes = ("a#", "button#", "a.", "button.")
		return (
			label.strip() != ""
			and not any(tag in selector.lower() for tag in non_actions)
			and selector.strip().startswith(interactive_prefixes)
		)

	seen_labels = set()
	deduped_dom = []
	for el in dom_elements:
		if ' - ' not in el:
			continue
		label = el.split(' - ')[-1].strip()
		selector = el.split(' - ')[0].strip()
		if label.lower().startswith("collapse"):
			continue
		if is_interactive(label, selector) and label not in seen_labels:
			deduped_dom.append(el)
			seen_labels.add(label)

	prompt = _build_prompt(instruction, deduped_dom)
	debug_log(f"🧠 LLM Prompt:\n{prompt}")
	response = run_local_llm(prompt)
	debug_log(f"🧠 LLM Full Response:\n{response}")

	label = response.strip().splitlines()[0].strip().strip("'").strip('"')

	def _is_label_match(a, b):
		a = a.strip().strip("'").strip('"').lower()
		b = b.strip().strip("'").strip('"').lower()
		return SequenceMatcher(None, a, b).ratio() > 0.9

	best_selector = None
	for el in deduped_dom:
		selector, el_label = el.split(' - ')
		if _is_label_match(el_label, label):
			best_selector = selector.strip()
			break
	else:
		raise ValueError(f"❌ LLM returned label '{label}' not found in visible elements")

	debug_log("Exited")

	def _partial_match(sel: str, el: str) -> bool:
		id_match = "#" in sel and sel.split("#")[-1].split()[0] in el
		class_match = "." in sel and any(cls in el for cls in sel.split(".")[1:])
		return id_match or class_match

	matched_element = next(
		(el for el in deduped_dom if best_selector in el),
		next((el for el in deduped_dom if _partial_match(best_selector, el)), "❓ No DOM match for selector")
	)
	debug_log(f"🧩 Matched element (fallback aware): {matched_element}")
	return best_selector, matched_element, label

def split_instruction(instruction: str, dom_elements: list[str]) -> list[str]:
	debug_log("Entered")

	if not instruction or not dom_elements:
		raise ValueError("Instruction and DOM elements must be provided")

	labels_only = sorted(set(el.split(' - ')[-1].strip() for el in dom_elements if ' - ' in el))
	label_block = "\n".join(f"- {label}" for label in labels_only)

	prompt = f"""
You are an Oracle Cloud QA Test Planner.

Given the visible UI labels and a test instruction, break the instruction into a numbered list of discrete UI steps. Each step should be a single user action. Use only labels from the visible list.

Instruction:
{instruction}

Visible labels:
{label_block}

Return only the numbered list of steps. Do not explain. Do not add extra steps.
"""
	debug_log(f"🧠 Step Split Prompt:\n{prompt}")
	response = run_local_llm(prompt)
	debug_log(f"🧠 Step Split LLM Response:\n{response}")
	debug_log("Exited")

	steps = [line.strip() for line in response.strip().splitlines() if line.strip()]
	return steps

def _build_prompt(instruction: str, dom_elements: list[str]) -> str:
	labels_only = sorted(set(el.split(' - ')[-1].strip() for el in dom_elements if ' - ' in el))
	label_block = "\n".join(f"- {label}" for label in labels_only)

	return f"""You are an expert Oracle Cloud test automation assistant.

Your task is to find the best label from a list of visible elements that best matches a test instruction.

Instruction:
{instruction}

Here are the currently visible labels:
{label_block}

Return ONLY the label that best matches the instruction. No explanations. No alternatives.
If nothing matches, return an empty string.
"""

def _extract_selector(response: str, dom_elements: list[str]) -> str:
	lines = [line.strip() for line in response.strip().splitlines() if line.strip()]
	for label in lines:
		for el in dom_elements:
			selector, el_label = el.split(' - ')
			if el_label.strip().lower() == label.lower():
				return selector.strip()
		debug_log(f"⚠️ Rejected hallucinated label: {label}")
	raise ValueError("❌ No valid selector returned (label not found)")
