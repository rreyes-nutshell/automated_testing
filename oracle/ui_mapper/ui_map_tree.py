from flask import Blueprint, render_template, request
from utils.logging import debug_log
from utils.db_utils import get_db_connection

ui_map_tree_bp = Blueprint("ui_map_tree", __name__, url_prefix="/ui-map/tree")

@ui_map_tree_bp.route("/<int:session_id>")
def display_ui_tree(session_id):
	debug_log("Entered")
	conn = get_db_connection()
	cur = conn.cursor()

	cur.execute("""
		SELECT i.id, i.parent_item_id, i.label, i.xpath, i.css_selector, i.tag_name
		FROM ui_path_items i
		JOIN ui_paths p ON i.ui_path_id = p.id
		JOIN ui_crawl_sessions s ON p.crawl_session_id = s.id
		WHERE s.id = %s
		ORDER BY i.ui_path_id, i.sequence_order
	""", (session_id,))

	nodes = cur.fetchall()
	cur.close()
	conn.close()

	node_map = {}
	root_nodes = []
	for row in nodes:
		id, parent_id, label, xpath, css_selector, tag = row
		node = {
			"id": id,
			"parent_id": parent_id,
			"label": label,
			"xpath": xpath,
			"css_selector": css_selector,
			"tag": tag,
			"children": []
		}
		node_map[id] = node
		if parent_id:
			node_map[parent_id]["children"].append(node)
		else:
			root_nodes.append(node)

	debug_log("Exited")
	return render_template("ui_map_tree.html", tree=root_nodes, session_id=session_id)
