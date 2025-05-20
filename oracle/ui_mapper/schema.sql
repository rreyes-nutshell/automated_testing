CREATE TABLE oracle_ui_map (
	id SERIAL PRIMARY KEY,
	module_name TEXT,
	selector TEXT,
	url TEXT,
	label TEXT,
	category TEXT,
	page_title TEXT,
	captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

