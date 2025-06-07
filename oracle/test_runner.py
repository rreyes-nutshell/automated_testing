# # <<01-JUN-2025:12:50>> - test_runner.py updated to wait generically before every click
# from typing import List, Dict, Any
# import json
# import re
# from pathlib import Path
# from datetime import datetime
# from flask import Blueprint, request, jsonify

# from utils.logging import debug_log
# from ai_helpers.plan_builder import llm_build_plan
# from ai_helpers.llm_utils import run_local_llm, sanitize_llm_json
# from ai_helpers.step_rewriter import rewrite_steps
# from oracle.navigation import load_ui_map, find_page_id_by_label, resolve_navigation_path
# from services.playwright_runner import run_browser_script

# oracle_test_runner_bp = Blueprint("oracle_test_runner_bp", __name__)


# @oracle_test_runner_bp.route("/run-test-script", methods=["POST"])
# @oracle_test_runner_bp.route("/", methods=["POST"])
# async def run_test_script():
#     debug_log("Entered")

#     try:
#         data = request.get_json()
#         script = data.get("llm_instruction") or data.get("script_text")
#         login_url = data.get("login_url")
#         username = data.get("username")
#         password = data.get("password")

#         if not script or not login_url:
#             return jsonify({"error": "Missing script_text or login_url"}), 400

#         debug_log("[parse_script_to_steps] Entered")

#         # 1) Build the one-pass plan via LLM
#         debug_log("[one_pass_llm] Entered")
#         try:
#             instructions_list = script.split("\n") if isinstance(script, str) else script
#             html_snapshot = ""  # login + page load happen inside run_browser_script
#             llm_plan = await llm_build_plan(instructions_list, html_snapshot)
#             llm_steps = llm_plan or []
#         except Exception as e:
#             debug_log(f"[one_pass_llm] ❌ Failed to build plan via LLM, falling back to empty list: {e}")
#             llm_steps = []
#         debug_log("[one_pass_llm] Exited")

#         # 2) Rewrite steps (mask credentials, normalize things, etc.)
#         rewritten = rewrite_steps(llm_steps, username, password)

#         # 3) Determine JSONL fallback (only if a valid click label exists)
#         click_steps = [s for s in rewritten if isinstance(s, dict) and s.get("action") == "click"]
#         target_label, parent_label = None, None
#         for i in range(len(click_steps) - 1, -1, -1):
#             if click_steps[i].get("label"):
#                 target_label = click_steps[i]["label"]
#                 if i > 0 and click_steps[i - 1].get("label"):
#                     parent_label = click_steps[i - 1]["label"]
#                 break

#         base_steps = []
#         try:
#             jsonl_path = Path(__file__).resolve().parent.parent / "oracle_ui_dump.jsonl"
#             nav_map = load_ui_map(str(jsonl_path))
#             debug_log("🧭 UI map loaded — building JSONL nav")
#             if target_label:
#                 page = find_page_id_by_label(nav_map, target_label, parent_label, require_actionable=True)
#                 page_id = page.get("page_id")
#                 path = resolve_navigation_path(nav_map, page_id)
#                 for p in path:
#                     base_steps.append({
#                         "action":   p["action_type"],
#                         "selector": p["selector"],
#                         "value":    p.get("value")
#                     })
#                 debug_log(f"🧭 JSONL nav steps: {len(base_steps)}")
#             else:
#                 debug_log("🧭 No target_label for JSONL nav; skipping")
#         except Exception as e:
#             debug_log(f"⚠️ JSONL nav error: {e}")

#         # 4) Choose which sequence to run: JSONL nav (if available) or LLM plan
#         steps_to_execute = base_steps if base_steps else rewritten

#         # 5) Before handing steps to Playwright, inject a wait_for_selector before every click
#         final_steps = []
#         for step in steps_to_execute:
#             if not isinstance(step, dict):
#                 continue

#             action = step.get("action")
#             selector = step.get("selector")
#             value = step.get("value", None)

#             if action == "click" and selector:
#                 # 5a) Wait generically until that selector appears
#                 final_steps.append({
#                     "action":   "wait_for_selector",
#                     "selector": selector,
#                     "value":    None
#                 })
#                 # 5b) Then perform the click
#                 final_steps.append({
#                     "action":   "click",
#                     "selector": selector,
#                     "value":    value
#                 })
#             else:
#                 # Any non-click action passes through unchanged
#                 final_steps.append(step)

#         # 6) Filter out any login-related steps (we let run_browser_script handle login)
#         filtered_steps = []
#         for step in final_steps:
#             sel = step.get("selector", "") or ""
#             if isinstance(step, dict) and (
#                 ("login" in sel) or sel in ["#username", "#password", "button[type=submit]"]
#             ):
#                 continue
#             filtered_steps.append(step)

#         # 7) Invoke Playwright: it will first log in (already_logged_in=False), then run filtered_steps
#         result = await run_browser_script(
#             steps=filtered_steps,
#             session_id=data.get("session_id"),
#             login_url=login_url,
#             username=username,
#             password=password,
#             preview_mode=data.get("preview_only", False),
#             target_label=target_label,
#             parent_label=parent_label,
#             already_logged_in=False
#         )
#         debug_log("Exited run_test_script")

#         # 8) Serialize result safely
#         try:
#             serializable_result = result if isinstance(result, (str, int, float, bool, list, dict)) else str(result)
#         except Exception:
#             serializable_result = str(result)

#         return jsonify({"status": "✅ Executed", "result": serializable_result})

#     except Exception as e:
#         debug_log(f"run_test_script ❌ Unexpected error: {e}")
#         return jsonify({"error": f"Unexpected server error: {e}"}), 500
# <<01-JUN-2025:12:50>> - test_runner.py updated to wait generically before every click
from typing import List, Dict, Any
import json
import re
from pathlib import Path
from datetime import datetime
from flask import Blueprint, request, jsonify

from utils.logging import debug_log
from ai_helpers.plan_builder import llm_build_plan
from ai_helpers.llm_utils import run_local_llm, sanitize_llm_json
from ai_helpers.step_rewriter import rewrite_steps
from oracle.navigation import load_ui_map, find_page_id_by_label, resolve_navigation_path
from services.playwright_runner import run_browser_script

oracle_test_runner_bp = Blueprint("oracle_test_runner_bp", __name__)


@oracle_test_runner_bp.route("/run-test-script", methods=["POST"])
@oracle_test_runner_bp.route("/", methods=["POST"])
async def run_test_script():
    debug_log("Entered")

    try:
        data = request.get_json()
        script = data.get("llm_instruction") or data.get("script_text")
        login_url = data.get("login_url")
        username = data.get("username")
        password = data.get("password")

        if not script or not login_url:
            return jsonify({"error": "Missing script_text or login_url"}), 400

        debug_log("[parse_script_to_steps] Entered")

        # 1) Build the one-pass plan via LLM
        debug_log("[one_pass_llm] Entered")
        try:
            instructions_list = script.split("\n") if isinstance(script, str) else script
            html_snapshot = ""  # login + page load happen inside run_browser_script
            llm_plan = await llm_build_plan(instructions_list, html_snapshot)
            llm_steps = llm_plan or []
        except Exception as e:
            debug_log(f"[one_pass_llm] ❌ Failed to build plan via LLM, falling back to empty list: {e}")
            llm_steps = []
        debug_log("[one_pass_llm] Exited")

        # 2) Rewrite steps (mask credentials, normalize things, etc.)
        # <<02-JUN-2025:00:00>> - Flatten test-case objects into individual steps before rewriting
        flat_llm_steps = []
        if isinstance(llm_steps, list):
            for case in llm_steps:
                flat_llm_steps.extend(case.get("steps", []))
        else:
            flat_llm_steps = llm_steps

        rewritten = rewrite_steps(flat_llm_steps, username, password)

        # 3) Determine JSONL fallback (only if a valid click label exists)
        click_steps = [s for s in rewritten if isinstance(s, dict) and s.get("action") == "click"]
        target_label, parent_label = None, None
        for i in range(len(click_steps) - 1, -1, -1):
            if click_steps[i].get("label"):
                target_label = click_steps[i]["label"]
                if i > 0 and click_steps[i - 1].get("label"):
                    parent_label = click_steps[i - 1]["label"]
                break

        base_steps = []
        try:
            jsonl_path = Path(__file__).resolve().parent.parent / "oracle_ui_dump.jsonl"
            nav_map = load_ui_map(str(jsonl_path))
            debug_log("🧭 UI map loaded — building JSONL nav")
            if target_label:
                page = find_page_id_by_label(nav_map, target_label, parent_label, require_actionable=True)
                page_id = page.get("page_id")
                path = resolve_navigation_path(nav_map, page_id)
                for p in path:
                    base_steps.append({
                        "action":   p["action_type"],
                        "selector": p["selector"],
                        "value":    p.get("value")
                    })
                debug_log(f"🧭 JSONL nav steps: {len(base_steps)}")
            else:
                debug_log("🧭 No target_label for JSONL nav; skipping")
        except Exception as e:
            debug_log(f"⚠️ JSONL nav error: {e}")

        # 4) Choose which sequence to run: JSONL nav (if available) or LLM plan
        steps_to_execute = base_steps if base_steps else rewritten

        # 5) Before handing steps to Playwright, inject a wait_for_selector before every click
        final_steps = []
        for step in steps_to_execute:
            if not isinstance(step, dict):
                continue

            action = step.get("action")
            selector = step.get("selector")
            value = step.get("value", None)

            if action == "click" and selector:
                # 5a) Wait generically until that selector appears
                final_steps.append({
                    "action":   "wait_for_selector",
                    "selector": selector,
                    "value":    None
                })
                # 5b) Then perform the click
                final_steps.append({
                    "action":   "click",
                    "selector": selector,
                    "value":    value
                })
            else:
                # Any non-click action passes through unchanged
                final_steps.append(step)

        # 6) Filter out any login-related steps (we let run_browser_script handle login)
        filtered_steps = []
        for step in final_steps:
            sel = step.get("selector", "") or ""
            if isinstance(step, dict) and (
                ("login" in sel) or sel in ["#username", "#password", "button[type=submit]"]
            ):
                continue
            filtered_steps.append(step)

        # 7) Invoke Playwright: it will first log in (already_logged_in=False), then run filtered_steps
        result = await run_browser_script(
            steps=filtered_steps,
            session_id=data.get("session_id"),
            login_url=login_url,
            username=username,
            password=password,
            preview_mode=data.get("preview_only", False),
            target_label=target_label,
            parent_label=parent_label,
            already_logged_in=False
        )
        debug_log("Exited run_test_script")

        # 8) Serialize result safely
        try:
            serializable_result = result if isinstance(result, (str, int, float, bool, list, dict)) else str(result)
        except Exception:
            serializable_result = str(result)

        return jsonify({"status": "✅ Executed", "result": serializable_result})

    except Exception as e:
        debug_log(f"run_test_script ❌ Unexpected error: {e}")
        return jsonify({"error": f"Unexpected server error: {e}"}), 500
