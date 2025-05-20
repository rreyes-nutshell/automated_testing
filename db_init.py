import os
from flask import Flask, render_template
from routes import register_blueprints
from utils.logging import debug_log
from dotenv import load_dotenv
import psycopg2

# Load .env from instance/ folder
base_dir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(base_dir, "instance", ".env")
if not os.path.exists(env_path):
    env_path = os.path.join(base_dir, "..", "instance", ".env")
load_dotenv(env_path)

def init_db():
    print("📢 DATABASE_URL loaded as:", os.getenv("DATABASE_URL"))
    debug_log("Entered")
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS test_sessions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        script_name TEXT,
        created_by TEXT,
        creation_date TIMESTAMP DEFAULT now(),
        last_updated_by TEXT,
        last_update_date TIMESTAMP DEFAULT now()
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS test_steps (
        id SERIAL PRIMARY KEY,
        session_id UUID REFERENCES test_sessions(id),
        step_number INTEGER,
        instruction TEXT,
        status TEXT,
        result TEXT,
        creation_date TIMESTAMP DEFAULT now(),
        created_by TEXT,
        last_update_date TIMESTAMP DEFAULT now(),
        last_updated_by TEXT
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
    debug_log("Exited")

if __name__ == "__main__":
    init_db()
