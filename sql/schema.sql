-- sql/schema.sql

CREATE TABLE IF NOT EXISTS ui_pages (
	id SERIAL PRIMARY KEY,
	page_name TEXT,
	selector TEXT,
	url TEXT,
	category TEXT,
	captured_at TIMESTAMP,
        page_id TEXT,
        crawler_name TEXT,
        session_id TEXT,
        is_external BOOLEAN DEFAULT false,
	has_real_url BOOLEAN DEFAULT false,
	aria_label TEXT,
	title_attr TEXT,
	is_skipped BOOLEAN DEFAULT false,
	version TEXT,
	creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	created_by TEXT DEFAULT 'system',
	last_update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	last_updated_by TEXT DEFAULT 'system'
);


CREATE TABLE IF NOT EXISTS ui_page_roles (
	id SERIAL PRIMARY KEY,
	page_id INTEGER REFERENCES ui_pages(id) ON DELETE CASCADE,
	role TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ui_page_actions (
	id SERIAL PRIMARY KEY,
	page_id INTEGER REFERENCES ui_pages(id) ON DELETE CASCADE,
	action TEXT NOT NULL
);

CREATE TABLE ui_map (
	id SERIAL PRIMARY KEY,
	label TEXT NOT NULL,
	parent_label TEXT,
	selector TEXT,
	page_id TEXT UNIQUE,
	action_type TEXT,
	value TEXT,
	url TEXT,
	category TEXT,
	role_visibility TEXT[],
	is_actionable BOOLEAN DEFAULT true,
	is_skipped BOOLEAN DEFAULT false,
	captured_at TIMESTAMP DEFAULT NOW(),
	created_by TEXT,
	creation_date TIMESTAMP DEFAULT NOW(),
	last_updated_by TEXT,
	last_update_date TIMESTAMP DEFAULT NOW()
);
