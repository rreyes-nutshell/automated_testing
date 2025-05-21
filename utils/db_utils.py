# utils/db_utils.py

import os
import psycopg2
from utils.logging import debug_log


def _connect_via_url(database_url):
    """Return psycopg2 connection using DATABASE_URL."""
    return psycopg2.connect(database_url)

def get_db_connection():
    """Return a psycopg2 connection using env vars or DATABASE_URL."""
    debug_log("Entered")

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        conn = _connect_via_url(database_url)
    else:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", 5432),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )

    params = conn.get_dsn_parameters()
    debug_log(
        f"Connected to database {params.get('dbname')} at {params.get('host')}:{params.get('port')}"
    )
    debug_log("Exited")
    return conn
