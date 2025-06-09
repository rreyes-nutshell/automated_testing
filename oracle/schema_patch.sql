-- <<08-JUN-2025:21:30>> - Missing table additions for Oracle UI crawler

-- Crawl sessions
CREATE TABLE IF NOT EXISTS ui_automation.ui_crawl_sessions (
	id SERIAL PRIMARY KEY,
	username TEXT NOT NULL,
	is_superuser BOOLEAN DEFAULT FALSE,
	session_note TEXT,
	session_id UUID NOT NULL,
	created_by TEXT NOT NULL,
	creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	last_updated_by TEXT,
	last_update_date TIMESTAMP
);

-- UI paths within each crawl session
CREATE TABLE IF NOT EXISTS ui_automation.ui_paths (
	id SERIAL PRIMARY KEY,
	crawl_session_id INT NOT NULL REFERENCES ui_automation.ui_crawl_sessions(id) ON DELETE CASCADE,
	path_name TEXT NOT NULL,
	created_by TEXT,
	creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Individual path items (DOM elements)
CREATE TABLE IF NOT EXISTS ui_automation.ui_path_items (
	id SERIAL PRIMARY KEY,
	ui_path_id INT NOT NULL REFERENCES ui_automation.ui_paths(id) ON DELETE CASCADE,
	parent_item_id INT,
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
	is_clickable BOOLEAN,
	classification TEXT,
	created_by TEXT,
	crawler_session_id INT
);

-- Per-user visibility toggles (optional)
CREATE TABLE IF NOT EXISTS ui_automation.user_visible_paths (
	id SERIAL PRIMARY KEY,
	username TEXT,
	ui_path_item_id INT REFERENCES ui_automation.ui_path_items(id) ON DELETE CASCADE,
	crawl_session_id INT,
	visible BOOLEAN DEFAULT TRUE,
	visibility_reason TEXT,
	creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
