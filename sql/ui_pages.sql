DROP TABLE ui_pages CASCADE;

CREATE TABLE ui_pages (
	id SERIAL PRIMARY KEY,
	page_name TEXT NOT NULL,               -- from label
	page_id TEXT,                          -- from JSON key: page_id
	url TEXT NOT NULL,
	selector TEXT,
	category TEXT,
	version TEXT DEFAULT 'unknown',
	is_external BOOLEAN DEFAULT FALSE,
	has_real_url BOOLEAN DEFAULT FALSE,
	aria_label TEXT,
	title_attr TEXT,
	captured_at TIMESTAMP,
	is_skipped BOOLEAN DEFAULT FALSE,

	-- audit columns
	creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	created_by TEXT DEFAULT 'system',
	last_update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	last_updated_by TEXT DEFAULT 'system',

	-- prevent duplicate inserts during import
	UNIQUE (page_name, url)
);
