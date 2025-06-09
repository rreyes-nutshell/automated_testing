# utils/db_utils.py

import os
import psycopg2
from dotenv import load_dotenv
from utils.logging import debug_log

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Load .env from the root
load_dotenv(os.path.join(root_dir, '.env'))

def _connect_via_url(database_url):
    """Return psycopg2 connection using DATABASE_URL."""
    return psycopg2.connect(database_url)

def get_db_connection():
    # debug_log("Entered x")
    database_url = os.getenv("DATABASE_URL")
    # debug_log(f"DATABASE_URL loaded as: {database_url}")
    if database_url:
        conn = psycopg2.connect(database_url)
    else:
        # debug_log("No DATABASE_URL found, using individual parameters")
        # debug_log(
        #     f"Connecting to database {os.getenv('DB_NAME')} at {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
        # )
        # debug_log(
        #     f"Using user {os.getenv('DB_USER')} and password {os.getenv('DB_PASSWORD')}"
        # )

        conn = psycopg2.connect(
            # host=os.getenv("DB_HOST", "localhost"),
            host='localhost',
            port=os.getenv("DB_PORT", 5432),
            dbname=os.getenv("UI_DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
    # debug_log(
    #     f"Connected to database {os.getenv('DB_NAME')} at {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
    # )
    # debug_log("Exited")
    return conn

# <<08-JUN-2025:20:01>> - Added UI schema/table creation support

def create_ui_schema_and_tables():
	debug_log("Entered create_ui_schema_and_tables")
	conn = get_db_connection()
	try:
		with conn.cursor() as cur:
			# Create schema if not exists
			cur.execute("""
				CREATE SCHEMA IF NOT EXISTS ui_automation;
			""")

			# UI Pages
			cur.execute("""
				CREATE TABLE IF NOT EXISTS ui_automation.ui_pages (
					id SERIAL PRIMARY KEY,
					page_id TEXT NOT NULL,
					label TEXT,
					role TEXT,
					context TEXT,
					url TEXT,
					raw_json JSONB,
					created_at TIMESTAMP DEFAULT NOW()
				);
			""")

			# Navigation Graph
			cur.execute("""
				CREATE TABLE IF NOT EXISTS ui_automation.ui_graph_edges (
					id SERIAL PRIMARY KEY,
					from_page_id TEXT NOT NULL,
					to_page_id TEXT NOT NULL,
					selector TEXT,
					nav_label TEXT,
					created_at TIMESTAMP DEFAULT NOW()
				);
			""")

			# Session Logs
			cur.execute("""
				CREATE TABLE IF NOT EXISTS ui_automation.ui_session_logs (
					id SERIAL PRIMARY KEY,
					session_id TEXT NOT NULL,
					step_index INT,
					action TEXT,
					selector TEXT,
					status TEXT,
					output TEXT,
					created_at TIMESTAMP DEFAULT NOW()
				);
			""")

			# Optional: Snapshot dump
			cur.execute("""
				CREATE TABLE IF NOT EXISTS ui_automation.ui_snapshots (
					id SERIAL PRIMARY KEY,
					session_id TEXT NOT NULL,
					step_index INT,
					html TEXT,
					screenshot_path TEXT,
					created_at TIMESTAMP DEFAULT NOW()
				);
			""")

		conn.commit()
		debug_log("✅ UI schema and tables created successfully")
	finally:
		conn.close()
		debug_log("Exited create_ui_schema_and_tables")
