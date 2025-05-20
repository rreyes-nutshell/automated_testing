# utils/bootstrap_db.py
import os
import psycopg2
from utils.logging import debug_log

def bootstrap_schema():
	debug_log("Entered")

	conn = psycopg2.connect(
		dbname=os.getenv("DB_NAME"),
		user=os.getenv("DB_USER"),
		password=os.getenv("DB_PASSWORD"),
		host=os.getenv("DB_HOST"),
		port=os.getenv("DB_PORT", 5432)
	)

	with conn:
		with conn.cursor() as cur:
			with open("sql/schema.sql", "r") as f:
				sql = f.read()
				cur.execute(sql)

	debug_log("✅ Schema bootstrap completed")
	debug_log("Exited")
