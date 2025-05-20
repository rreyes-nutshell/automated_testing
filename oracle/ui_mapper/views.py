# ui_mapper/views.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, send_file
from utils.logging import debug_log
from utils.db_utils import get_db_connection
from oracle.ui_mapper.importer import import_jsonl_to_db
from oracle.ui_mapper.exporter import export_db_to_jsonl
import os

ui_mapper_bp = Blueprint("ui_mapper", __name__, url_prefix="/ui-map", template_folder="templates")

@ui_mapper_bp.route("/")
def index():
	debug_log("Entered")
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("""
		SELECT id, page_name, url, version, is_skipped 
		FROM ui_pages 
		ORDER BY page_name
	""")
	pages = cur.fetchall()
	cur.close()
	conn.close()
	debug_log("Exited")
	return render_template("ui_mapper_index.html", pages=pages)


@ui_mapper_bp.route("/toggle/<int:page_id>", methods=["POST"])
def toggle_skip(page_id):
	debug_log("Entered")
	conn = get_db_connection()
	with conn.cursor() as cur:
		cur.execute("UPDATE ui_pages SET is_skipped = NOT is_skipped WHERE id = %s", (page_id,))
		conn.commit()
	conn.close()
	debug_log("Exited")
	return redirect(url_for("ui_mapper.index"))


@ui_mapper_bp.route("/import", methods=["POST"])
def import_jsonl():
	debug_log("Entered")
	file = request.files["jsonl_file"]
	if file.filename.endswith(".jsonl"):
		tmp_path = os.path.join("/tmp", file.filename)
		file.save(tmp_path)
		conn = get_db_connection()
		cur = conn.cursor()
		cur.execute("DELETE FROM ui_pages")
		conn.commit()
		cur.close()
		import_jsonl_to_db(tmp_path, conn)
		conn.close()
		flash("✅ Import successful", "success")
	else:
		flash("❌ Invalid file type. Please upload a .jsonl file", "danger")
	debug_log("Exited")
	return redirect(url_for("ui_mapper.index"))

@ui_mapper_bp.route("/export")
def export_jsonl():
	debug_log("Entered")
	tmp_path = "/tmp/exported_ui_map.jsonl"
	conn = get_db_connection()
	export_db_to_jsonl(tmp_path, conn)
	conn.close()
	debug_log("Exited")
	return send_file(tmp_path, mimetype="application/jsonl", as_attachment=True, download_name="ui_map.jsonl")


@ui_mapper_bp.route("/ui-map-index")
def show_ui_index():
	return render_template("ui_mapper_index.html")
