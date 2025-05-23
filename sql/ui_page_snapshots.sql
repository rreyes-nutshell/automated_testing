CREATE TABLE ui_page_snapshots (
	id SERIAL PRIMARY KEY,
	ui_path_id INT REFERENCES ui_paths(id) ON DELETE CASCADE,
	final_url TEXT,
	page_title TEXT,
	html_dump TEXT,
	created_by TEXT,
	creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
