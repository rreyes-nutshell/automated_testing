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


@ui_map_admin_bp.route("/")
def index():
        debug_log("Entered")
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
                """
                SELECT id, page_name, page_id, url, selector, category, version,
                       is_external, has_real_url, aria_label, title_attr,
                       captured_at, is_skipped, crawler_name, session_id
                FROM ui_pages
                ORDER BY page_name
                """
        )
        pages = cur.fetchall()
        cur.close()
        conn.close()
        session_id = request.args.get("session_id")
        debug_log("Exited")
        return render_template("ui_mapper_index.html", pages=pages, session_id=session_id)

@ui_map_admin_bp.route("/run-crawler", methods=["POST"])
def run_crawler():
        debug_log("Entered")

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
        asyncio.run(crawl_oracle_ui(username, password, crawler_name, session_id))

        debug_log("Exited")
        return redirect(url_for("ui_map_admin.index", session_id=session_id))



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
