import json
import os
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for
from utils.logging import debug_log
from oracle.login_steps import run_oracle_login_steps
from services.playwright_runner import run_browser_script

template_path = os.path.join(os.path.dirname(__file__), "templates")
ui_map_viewer_bp = Blueprint("ui_map_viewer_bp", __name__, template_folder=template_path)


@ui_map_viewer_bp.route("/ui-map", methods=["GET"])
def show_ui_map():
	debug_log("Entered")
	jsonl_path = Path(__file__).resolve().parent.parent / "oracle_ui_dump.jsonl"
	entries = []
	if not jsonl_path.exists():
		debug_log(f"❌ File not found: {jsonl_path}")
	else:
		with open(jsonl_path, "r", encoding="utf-8") as f:
			for line in f:
				try:
					entry = json.loads(line)
					if entry.get("is_actionable"):
						entries.append(entry)
				except:
					continue
	debug_log("Exited")
	return render_template("ui_mapper_index.html", pages=entries)


@ui_map_viewer_bp.route("/ui-map/run", methods=["POST"])
async def run_selected_ui_item():
	debug_log("Entered")
	selector = request.form.get("selector")
	username = request.form.get("username")
	password = request.form.get("password")
	login_url = request.form.get("login_url")

	steps = [
		{"action": "goto", "value": login_url},
		{"action": "fill", "selector": "input[name=userid]", "value": username},
		{"action": "fill", "selector": "input[name=password]", "value": password},
		{"action": "click", "selector": "button[type=submit]"},
		{"action": "wait_for_selector", "selector": selector},
		{"action": "click", "selector": selector},
		{"action": "screenshot", "value": None},
		{"action": "log_result", "value": None}
	]

	result_html = await run_browser_script(
		steps,
		session_id="manual_ui_test",
		login_url=login_url,
		username=username,
		password=password
	)
	debug_log("Exited")
	return redirect(url_for("ui_map_viewer_bp.show_ui_map"))
