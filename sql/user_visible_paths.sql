CREATE TABLE user_visible_paths (
	id SERIAL PRIMARY KEY,
	username TEXT NOT NULL,
	ui_path_item_id INT REFERENCES ui_path_items(id) ON DELETE CASCADE,
	crawl_session_id INT REFERENCES ui_crawl_sessions(id) ON DELETE CASCADE,
	visible BOOLEAN DEFAULT TRUE,
	visibility_reason TEXT, -- e.g. "menu hidden", "page load error", "no access"
	creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
