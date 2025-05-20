import os
import psycopg2
from dotenv import load_dotenv
from utils.logging import debug_log

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def save_test_case(session_id, sheet, test_case, step_number, step_text, created_by="system"):
    debug_log("Entered")
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO test_cases (
            session_id, sheet_name, test_case_name, step_number,
            step_text, created_by, last_updated_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (session_id, sheet, test_case, step_number, step_text, created_by, created_by))

    conn.commit()
    cur.close()
    conn.close()
    debug_log("Exited")