from utils.logging import debug_log
import re


def sanitize_selector(selector):
	if not selector:
		return selector

	# Remove surrounding quotes
	selector = selector.strip("\"").strip("'")

	# Remove unsupported pseudo-classes like :contains(...)
	selector = re.sub(r':contains\([^)]*\)', '', selector)

	# Fix broken CSS selector parts like 'aTools' or 'aScheduled Processes'
	selector = re.sub(r'([a-zA-Z]+)([A-Z][a-z]+)', r'\1 \2', selector)

	# Clean excessive spaces
	selector = re.sub(r'\s+', ' ', selector).strip()

	return selector


def normalize_selector(selector):
	"""Alias for sanitize_selector to preserve backwards compatibility."""
	return sanitize_selector(selector)


def normalize_steps(steps, login_url=None):
	debug_log("Entered")

	if steps and steps[0].get("action") != "goto" and login_url:
		steps.insert(0, {
			"action": "goto",
			"value": login_url
		})

	for step in steps:
		if 'selector' in step:
			step['selector'] = sanitize_selector(step['selector'])
		if 'value' in step and isinstance(step['value'], str):
			step['value'] = step['value'].strip('"').strip("'")

	debug_log("Exited")
	return steps
