# import asyncio
# from flask import Blueprint, request, jsonify
# from utils.logging import debug_log
# from services.playwright_runner import run_browser_script
# from oracle.login_script import oracle_login


# playwright_routes_bp = Blueprint('playwright_routes_bp', __name__)

# @playwright_routes_bp.route("/run-oracle-login", methods=["POST"])
# def run_oracle_login():
#     debug_log("Entered")
#     data = request.json
#     username = data.get("username")
#     password = data.get("password")
#     login_url = data.get("login_url")

#     if not all([username, password, login_url]):
#         return jsonify({"error": "Missing parameters"}), 400

#     result = asyncio.run(run_browser_script(oracle_login, username, password, login_url))

#     if result:
#         debug_log(f"✅ Oracle login result received ({len(result)} chars)")
#     else:
#         debug_log("⚠️ Oracle login result was empty or None")

#     debug_log("Exited")
#     return jsonify({
#         "result": "✅ Script executed",
#         "content": result or "⚠️ No content returned"
#     })
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

# <<02-JUN-2025:21:50>> – Added helper function for checkbox toggling directly into routes to avoid circular imports
# async def toggle_checkbox_under_section(page, label: str, section: str, check: bool = True):
#     """
#     Toggles a checkbox by its ARIA name under a given table/row context.
#     Parameters:
#       - page: Playwright Page object
#       - label: The visible checkbox label (e.g., "Select All" or invoice number)
#       - section: The parent row or table name (e.g., "Invoices on Hold")
#       - check: True to check, False to uncheck
#     """
#     debug_log(f"Entered: toggle_checkbox_under_section(label='{label}', section='{section}', check={check})")
#     # Scope under the row named "section"
#     row_locator = page.get_by_role("row", name=section)
#     checkbox = row_locator.get_by_role("checkbox", name=label)
#     if check:
#         await checkbox.check()
#     else:
#         await checkbox.uncheck()
#     debug_log(f"Exited: toggle_checkbox_under_section(label='{label}', section='{section}', check={check})")
