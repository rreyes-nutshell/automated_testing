CREATE TABLE ui_paths (
	id SERIAL PRIMARY KEY,
	crawl_session_id INT REFERENCES ui_crawl_sessions(id) ON DELETE CASCADE,
	path_name TEXT,
	created_by TEXT,
	creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
