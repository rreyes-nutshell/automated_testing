# utils/db_utils.py

import psycopg2
import os
from utils.logging import debug_log

def get_db_connection():
	debug_log("Entered")
	conn = psycopg2.connect(
		host=os.getenv("DB_HOST", "localhost"),
		port=os.getenv("DB_PORT", 5432),
		dbname=os.getenv("DB_NAME"),
		user=os.getenv("DB_USER"),
		password=os.getenv("DB_PASSWORD")
	)
	debug_log(f"Connected to database {os.getenv('DB_NAME')} at {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")	
	debug_log("Exited")
	return conn
