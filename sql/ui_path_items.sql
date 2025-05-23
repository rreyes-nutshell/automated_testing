CREATE TABLE ui_path_items (
	id SERIAL PRIMARY KEY,
	ui_path_id INT REFERENCES ui_paths(id) ON DELETE CASCADE,
	parent_item_id INT REFERENCES ui_path_items(id) ON DELETE CASCADE,
	sequence_order INT,
	
	label TEXT,
	element_id TEXT,
	class_name TEXT,
	tag_name TEXT,
	name_attr TEXT,
	role TEXT,
	aria_label TEXT,
	aria_describedby TEXT,
	href TEXT,
	dest_url TEXT,
	xpath TEXT,
	css_selector TEXT,
	inner_text TEXT,
	outer_html TEXT,
	click_action TEXT,
	is_clickable BOOLEAN DEFAULT FALSE,
	classification TEXT,

	created_by TEXT,
	creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	last_updated_by TEXT,
	last_update_date TIMESTAMP
);
