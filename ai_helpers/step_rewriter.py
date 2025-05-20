from utils.logging import debug_log, log_step_to_file
from datetime import datetime
from ai_helpers.step_utils import post_login_validation_steps


NAV_LINKS = [
	"Scheduled Processes",
	"Show More",
	"Tools",
	"Home",
	"Reports and Analytics",
	"Financial Reporting Center"
	# Add more Oracle nav targets here as needed
]

def build_login_steps(username, password):
	return [
		{"action": "wait_for_selector", "selector": "input[name='userid']"},
		{"action": "fill", "selector": "input[name='userid']", "value": username},
		{"action": "fill", "selector": "input[name='password']", "value": password},
		{"action": "wait_for_selector", "selector": "button#btnActive"},
		{"action": "evaluate_click", "selector": "button#btnActive"},
		{"action": "wait_for_timeout", "value": "3000"},
		{"action": "wait_for_url", "value": "https://.*oraclecloud.com/.*Welcome.*"},
		{"action": "wait_for_selector", "selector": "text='Sign Out'"},
	]


def rewrite_steps(steps, username=None, password=None, session_id=None):
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	debug_log("Entered")
	rewritten = []
	login_inserted = False
	show_more_injected = False

	for i, step in enumerate(steps):
		orig_selector = step.get("selector") or ""
		orig_action = step.get("action", "")
		value = step.get("value", "")

		# Detect login sequence
		if not login_inserted and orig_action == "fill" and "userid" in orig_selector:
			debug_log("🔐 Injecting isolated login steps")
			rewritten.extend(build_login_steps(username or "", password or ""))
			login_inserted = True
			continue

		# Rewrite bad goto to click
		if orig_action == "goto" and orig_selector and not orig_selector.startswith("http"):
			step["action"] = "click"

		# Normalize any known Oracle navigation link by name
		if any(label in orig_selector for label in NAV_LINKS) or (step.get("name") in NAV_LINKS):
			label = next(label for label in NAV_LINKS if label in orig_selector or step.get("name") == label)
			step = {"action": "click_by_role", "role": "link", "name": label}

		# After Navigator click, inject Show More logic only once
		if not show_more_injected and step["action"] == "click" and "Navigator" in step.get("selector", ""):
			rewritten.append(step)
			rewritten.append({"action": "wait_for_timeout", "value": "2000"})
			rewritten.append({"action": "log_html", "value": "after_navigator"})
			rewritten.append({"action": "screenshot", "value": "after_navigator"})
			rewritten.append({"action": "debug_pause"})
			rewritten.append({"action": "wait_for_selector", "selector": "get_by_role(\"link\", name=\"Show More\")", "value": "visible"})
			rewritten.append({"action": "click_by_role", "role": "link", "name": "Show More"})
			rewritten.append({"action": "wait_for_timeout", "value": "1000"})
			show_more_injected = True
			continue

		# Skip any redundant 'Tools' clicks if Show More was already clicked
		if show_more_injected and step.get("name") == "Tools":
			debug_log("⏭️ Skipping redundant Tools step after Show More")
			continue

		debug_log(f"Rewriting step: {step}")
		rewritten.append(step)
		log_step_to_file("rewrite", step, session_id=session_id)

		# Add pause after Tools click (optional)
		if step["action"] == "click" and 'cl1' in step.get("selector", ""):
			rewritten.append({"action": "wait_for_timeout", "value": "2000"})

	# Add screenshot + success marker
	rewritten.append({"action": "screenshot", "value": f"final_state_{timestamp}"})
	rewritten.append({"action": "log_result", "value": "✅ Navigation successful"})

	debug_log("Exited")
	return rewritten
