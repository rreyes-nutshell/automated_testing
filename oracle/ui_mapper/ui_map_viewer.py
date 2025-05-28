import json
import os
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for
from utils.logging import debug_log
from utils.db_utils import get_db_connection
from oracle.login_steps import run_oracle_login_steps
from services.playwright_runner import run_browser_script
from dotenv import load_dotenv
import dotenv



template_path = os.path.join(os.path.dirname(__file__), "templates")
ui_map_viewer_bp = Blueprint("ui_map_viewer_bp", __name__, template_folder=template_path)


root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(root_dir, '.env'))

dotenv.dotenv_values(os.path.join(root_dir, '.env'))
# @ui_map_viewer_bp.route("/ui-map", methods=["GET"])
# def show_ui_map():
# 	debug_log("Entered")
# 	jsonl_path = Path(__file__).resolve().parent.parent / "oracle_ui_dump.jsonl"
# 	entries = []
# 	if not jsonl_path.exists():
# 		debug_log(f"❌ File not found: {jsonl_path}")
# 	else:
# 		with open(jsonl_path, "r", encoding="utf-8") as f:
# 			for line in f:
# 				try:
# 					entry = json.loads(line)
# 					if entry.get("is_actionable"):
# 						entries.append(entry)
# 				except:
# 					continue
# 	debug_log("Exited")
# 	return render_template("ui_mapper_index.html", pages=entries)

# inside ui_map_viewer.py or equivalent

load_dotenv()

@ui_map_viewer_bp.route("/ui-map", methods=["GET"])
def show_ui_map():
	debug_log("Entered")
	
	ora_user = os.getenv("ORA_USER")
	ora_pw = os.getenv("ORA_PW")
	ora_url = os.getenv("ORA_URL", "https://login-ibnijb-dev1.fa.ocs.oraclecloud.com")

	# existing logic to fetch pages:
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("""
		SELECT 
			id, page_name, page_id, url, locator, 
			category, version, is_external, has_real_url, 
			aria_label, title_attr, captured_at, is_skipped, 
			crawler_name, session_id
		FROM ui_pages
		ORDER BY session_id DESC, page_name ASC
	""")

	pages = cur.fetchall()
	cur.close()
	conn.close()

	debug_log("Exited")
	return render_template(
		"ui_mapper_index.html",
		pages=pages,
		ora_user=ora_user,
		ora_pw=ora_pw,
		ora_url=ora_url
	)


@ui_map_viewer_bp.route("/ui-map/run", methods=["POST"])
async def run_selected_ui_item():
	debug_log("Entered")
	selector = request.form.get("selector")
	debug_log(f"Selector: {selector}")	
	username = request.form.get("username")
	debug_log(f"Username: {username}")
	password = request.form.get("password")
	debug_log(f"Password: {'*' * len(password) if password else 'None'}")

	login_url = request.form.get("login_url")

	steps = [
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
