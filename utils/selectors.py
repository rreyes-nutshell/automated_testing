import re
import string
from utils.logging import debug_log

def escape_css_selector(selector: str) -> str:
	"""
	Escapes invalid characters in CSS selectors for Playwright.
	- Strips numeric prefixes (e.g., "1. ") from LLM output
	- Removes trailing comments like (for OKCancel button)
	- Removes markdown blocks and JS-style comments
	- Normalizes escaped LLM artifacts like \_ or \\
	- Escapes all characters not valid in CSS identifiers
	Example: '1. #afr::DlgSrvPopupCtnr.ok' becomes '#afr\:\:DlgSrvPopupCtnr\.ok'
	
	Note: LLM-generated selectors often come from modules like runtime_selector.py or llm_utils.py,
	which generate and interpret step data using model prompts and JSON formatting. These selectors
	may include human-readable prefixes, backslash escapes, code fences, JS comments, or inline annotations.
	"""
	if not selector:
		return selector

	debug_log(f"Original selector: {selector}")

	# Clean up whitespace and numbering artifacts from LLMs or logs
	selector = selector.strip()
	selector = re.sub(r'^\d+\.\s*', '', selector)

	# Strip markdown-style code fences (e.g., ```css ... ```)
	selector = re.sub(r'^```[a-zA-Z]*\n?', '', selector)
	selector = re.sub(r'```$', '', selector)

	# Remove JS-style comments (e.g., // comment)
	selector = re.sub(r'//.*$', '', selector).strip()

	# Remove trailing parenthetical comments with trailing text
	selector = re.sub(r'\s*\([^)]*\)[^)]*$', '', selector)

	# Normalize escaped LLM-style characters like \_ or \\
	selector = selector.replace("\\_", "_").replace("\\\\", "\\")

	# Escape backslashes first (again, post-normalization)
	selector = selector.replace("\\", "\\\\")

	# CSS valid characters: letters, digits, hyphen, underscore
	valid_chars = string.ascii_letters + string.digits + "-_"

	# Escape any character that is printable but not valid in a CSS identifier
	escaped = ''.join(f'\\{c}' if c in string.printable and c not in valid_chars else c for c in selector)

	return escaped


def is_escaped(selector: str) -> bool:
	# Check for backslashes preceding known special characters (already escaped)
	return bool(re.search(r'\\[\\\[\]\(\):.#"\'/ ]', selector))

def ensure_escaped_selector(selector: str) -> str:
	if is_escaped(selector):
		return selector
	return escape_css_selector(selector)
