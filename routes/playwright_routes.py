import asyncio
from flask import Blueprint, request, jsonify
from utils.logging import debug_log
from services.playwright_runner import run_browser_script
from oracle.login_script import oracle_login


playwright_routes_bp = Blueprint('playwright_routes_bp', __name__)

@playwright_routes_bp.route("/run-oracle-login", methods=["POST"])
def run_oracle_login():
    debug_log("Entered")
    data = request.json
    username = data.get("username")
    password = data.get("password")
    login_url = data.get("login_url")

    if not all([username, password, login_url]):
        return jsonify({"error": "Missing parameters"}), 400

    result = asyncio.run(run_browser_script(oracle_login, username, password, login_url))

    if result:
        debug_log(f"✅ Oracle login result received ({len(result)} chars)")
    else:
        debug_log("⚠️ Oracle login result was empty or None")

    debug_log("Exited")
    return jsonify({
        "result": "✅ Script executed",
        "content": result or "⚠️ No content returned"
    })
