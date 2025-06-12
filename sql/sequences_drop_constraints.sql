drop table  ui_automation.ui_pages;

CREATE TABLE IF NOT EXISTS ui_automation.ui_pages (
	id SERIAL PRIMARY KEY,
	session_id INTEGER NOT NULL,
	session_name TEXT NOT NULL,
	path_id INTEGER NOT NULL,
	url TEXT NOT NULL,
	page_title TEXT,
	page_heading TEXT,
	page_description TEXT,
	created_at TIMESTAMP DEFAULT now()
);

    
    

CREATE SEQUENCE ui_automation.ui_pages_id_seq
	INCREMENT BY 1
	MINVALUE 1
	START WITH 1
	CACHE 1;

DO $$ 
DECLARE
	rec RECORD;
BEGIN
	FOR rec IN 
		SELECT conname, conrelid::regclass AS table_name
		FROM pg_constraint
		WHERE contype = 'f'
		  AND connamespace = 'ui_automation'::regnamespace
	LOOP
		EXECUTE format('ALTER TABLE %s DROP CONSTRAINT %I', rec.table_name, rec.conname);
		RAISE NOTICE 'Dropped constraint % on table %', rec.conname, rec.table_name;
	END LOOP;
END $$;


CREATE TABLE IF NOT EXISTS ui_automation.ui_elements
(
    id integer NOT NULL DEFAULT nextval('ui_automation.ui_elements_id_seq'::regclass),
    page_url text COLLATE pg_catalog."default",
    label text COLLATE pg_catalog."default",
    tag_name text COLLATE pg_catalog."default",
    element_type text COLLATE pg_catalog."default",
    xpath text COLLATE pg_catalog."default",
    css_selector text COLLATE pg_catalog."default",
    session_id text COLLATE pg_catalog."default",
    created_at timestamp without time zone DEFAULT now(),
    page_id integer,
    CONSTRAINT ui_elements_pkey PRIMARY KEY (id),
    CONSTRAINT ui_elements_page_id_fkey FOREIGN KEY (page_id)
        REFERENCES ui_automation.ui_pages (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE ui_automation.ui_elements
    OWNER to nsadmin;



CREATE SEQUENCE ui_automation.ui_elements_id_seq
	INCREMENT BY 1
	MINVALUE 1
	START WITH 1
	CACHE 1;
