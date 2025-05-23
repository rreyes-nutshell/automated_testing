CREATE TABLE ui_crawl_sessions (
	id SERIAL PRIMARY KEY,
	username TEXT NOT NULL,
	is_superuser BOOLEAN DEFAULT FALSE,
	session_note TEXT,
	start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	end_time TIMESTAMP,
	created_by TEXT,
	creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
