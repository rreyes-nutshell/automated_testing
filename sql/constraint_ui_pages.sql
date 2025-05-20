ALTER TABLE ui_pages ADD CONSTRAINT unique_page_url UNIQUE (page_name, url);
