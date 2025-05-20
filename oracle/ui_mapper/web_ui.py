import sys
import os
import threading
from flask import Flask, render_template, request, redirect, url_for

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from oracle.ui_mapper.main import run_with_params, cancel_crawl
from oracle.ui_mapper.views import ui_mapper_bp
from utils.logging import debug_log

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback_secret_key")

# from oracle.ui_mapper.ui_map_admin import ui_map_admin_bp
# app.register_blueprint(ui_map_admin_bp)

latest_log_lines = []

# Register UI Mapper blueprint
app.register_blueprint(ui_mapper_bp)

def append_log(msg):
	debug_log("Entered")
	latest_log_lines.append(msg)
	if len(latest_log_lines) > 50:
		latest_log_lines.pop(0)
	debug_log("Exited")

@app.route("/", methods=["GET", "POST"])
def login():
	debug_log("Entered")
	if request.method == "POST":
		username = request.form.get("username", "").strip()
		password = request.form.get("password", "").strip()
		login_url = request.form.get("login_url", "").strip()

		try:
			threading.Thread(
				target=run_with_params,
				args=(login_url, username, password, append_log),
				daemon=True
			).start()
		except Exception as e:
			append_log(f"❌ Error starting crawl thread: {str(e)}")

		debug_log("Exited")
		return redirect(url_for("status"))

	debug_log("Exited")
	return render_template("login.html")

@app.route("/status")
def status():
	debug_log("Entered")
	debug_log("Exited")
	return render_template("status.html", log_lines=latest_log_lines[-50:])

if __name__ == "__main__":
	debug_log("Entered")
	app.run(debug=True)
	debug_log("Exited")
