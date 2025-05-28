from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.logging import debug_log
from utils.db_utils import get_db_connection
# from utils.jsonl_exporter import export_db_to_jsonl
# from utils.jsonl_importer import import_jsonl_to_db
from oracle.ui_mapper.exporter import export_db_to_jsonl
from oracle.ui_mapper.importer import import_jsonl_to_db
import os
import asyncio

ui_map_admin_bp = Blueprint("ui_map_admin", __name__, url_prefix="/ui-map")

@ui_map_admin_bp.route("/ui-map")
def index():
	debug_log("Entered")

	session_id = request.args.get("session_id")
	selected_only = request.args.get("selected_only", "false").lower() == "true"
	include_skipped = request.args.get("include_skipped", "false").lower() == "true"

	# Load data directly from JSONL instead of querying the DB
	import json
	json_path = os.path.join("logs", f"ui_map_{session_id}.jsonl")
	if os.path.exists(json_path):
		with open(json_path) as f:
			pages = [json.loads(line) for line in f if line.strip()]
	else:
		flash("UI map file not found.", "danger")
		pages = []

	# Removed DB operations from JSON load flow
	debug_log("Exited")

	return render_template("ui_mapper_index.html", pages=pages, session_id=session_id)


@ui_map_admin_bp.route("/run-crawler", methods=["POST"])
def run_crawler():
	debug_log("Entered")

	login_url = request.form.get("login_url")
	if not login_url or not login_url.startswith("http"):
		flash(f"Invalid or missing login URL: {login_url}", "danger")
		return redirect(url_for("ui_map_admin.index"))

	username = request.form.get("username")
	password = request.form.get("password")
	crawler_name = request.form.get("crawler_name", "default")
	headerless = request.form.get("headerless", "true")
	os.environ["HEADLESS"] = headerless

	if not username or not password:
		flash("Missing credentials", "danger")
		return redirect(url_for("ui_map_admin.index"))

	from oracle.ui_mapper.crawler import crawl_oracle_ui
	import uuid
	session_id = str(uuid.uuid4())
	asyncio.run(crawl_oracle_ui(username, password, crawler_name, session_id=session_id, login_url=login_url))
	export_path = os.path.join("logs", f"ui_map_{session_id}.jsonl")
	import json
	if os.path.exists(export_path):
		with open(export_path) as f:
			pages = [json.loads(line) for line in f if line.strip()]
		debug_log(f"📝 UI map loaded in-memory from {export_path}")
		return render_template("ui_mapper_index.html", pages=pages, session_id=session_id)
	else:
		debug_log(f"❌ Export file not found: {export_path}")
		flash("UI map file not found.", "danger")
		return redirect(url_for("ui_map_admin.index"))


@ui_map_admin_bp.route("/crawl-path", methods=["POST"])
def crawl_path():
	debug_log("Entered")

	selector = request.form.get("selector")
	username = request.form.get("username")
	password = request.form.get("password")
	login_url = request.form.get("login_url")
	crawler_name = request.form.get("crawler_name", "pathcrawl")
	debug_log(f"Selector: {selector}")
	if not selector or not username or not password or not login_url:
		flash("Missing crawl path parameters", "danger")
		return redirect(url_for("ui_map_admin.index"))

	from oracle.ui_mapper.path_crawler import crawl_path_from_selector
	import uuid
	from oracle.ui_mapper.extractor import insert_crawl_session
	crawl_db_id, _ = insert_crawl_session(username, is_superuser=False, session_note="Path Crawl")
	debug_log(f"Selector 2: {selector}")	
	asyncio.run(crawl_path_from_selector(selector, username, password, login_url, crawler_name, crawl_db_id))
	debug_log(f"Selector 3: {selector}")
	debug_log("Exited")
	return redirect(url_for("ui_map_tree.display_ui_tree", session_id=crawl_db_id))



@ui_map_admin_bp.route("/export")
def export_jsonl():
	debug_log("Entered")
	path = "/tmp/exported_ui_map.jsonl"
	export_db_to_jsonl(path, get_db_connection())
	debug_log("Exited")
	return redirect(url_for("ui_map_admin.download_export"))


@ui_map_admin_bp.route("/download-export")
def download_export():
	debug_log("Entered")
	debug_log("Exited")
	return redirect("/tmp/exported_ui_map.jsonl")


@ui_map_admin_bp.route("/import", methods=["GET", "POST"])
def import_jsonl():
	debug_log("Entered")
	if request.method == "POST":
		file = request.files.get("file")
		if file and file.filename.endswith(".jsonl"):
			temp_path = "/tmp/uploaded_ui_map.jsonl"
			file.save(temp_path)
			import_jsonl_to_db(temp_path, get_db_connection())
			os.remove(temp_path)
		return redirect(url_for("ui_map_admin.index"))
	debug_log("Exited")
	return render_template("import_ui_map.html")


@ui_map_admin_bp.route("/delete/<int:page_id>", methods=["POST"])
def delete_page(page_id):
	debug_log("Entered")
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("DELETE FROM ui_pages WHERE id = %s", (page_id,))
	conn.commit()
	cur.close()
	conn.close()
	debug_log("Exited")
	return redirect(url_for("ui_map_admin.index"))

@ui_map_admin_bp.route("/results")
def show_results():
	session_id = request.args.get("session_id")
	debug_log("Entered /results")
	import uuid
	try:
		session_id = str(uuid.UUID(session_id))
	except (ValueError, AttributeError):
		flash("Invalid session ID", "danger")
		return redirect(url_for("ui_map_admin.index"))

	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("SELECT label, locator FROM ui_pages WHERE session_id = %s", (session_id,))
	rows = cur.fetchall()
	pages = [{"label": r[0], "locator": r[1]} for r in rows]
	cur.close()
	return render_template("ui_map_results.html", pages=pages, session_id=session_id)
