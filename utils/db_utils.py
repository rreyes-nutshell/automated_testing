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
    debug_log("Entered x")
    database_url = os.getenv("DATABASE_URL")
    debug_log(f"DATABASE_URL loaded as: {database_url}")
    if database_url:
        conn = psycopg2.connect(database_url)
    else:
        debug_log("No DATABASE_URL found, using individual parameters")
        debug_log(
            f"Connecting to database {os.getenv('DB_NAME')} at {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
        )
        debug_log(
            f"Using user {os.getenv('DB_USER')} and password {os.getenv('DB_PASSWORD')}"
        )

        conn = psycopg2.connect(
            # host=os.getenv("DB_HOST", "localhost"),
            host='localhost',
            port=os.getenv("DB_PORT", 5432),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
    debug_log(
        f"Connected to database {os.getenv('DB_NAME')} at {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
    )
    debug_log("Exited")
    return conn
