import json
import re
from pathlib import Path
from datetime import datetime
from flask import Blueprint, request, jsonify

from utils.logging import debug_log
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

        oracle_hint = ""
        if "oraclecloud.com" in login_url:
            oracle_hint = "You are an Oracle Cloud test automation expert using Playwright."

        prompt = (
            f"{oracle_hint}"
            "Convert the following instruction into a JSON object.\n"
            "Respond with ONLY a JSON array. Each element must be a step object.\n"
            "Each step object must include: action, selector, value (use null if not applicable), and label (e.g. \"Journals\"). Optionally include parent_label if relevant.\n"
            "Use double quotes for all property names and values.\n"
            "Wrap all keys and string values in double quotes. Do NOT include markdown, comments, or any explanation text.\n\n"
            f"Instruction:\n{script}"
        )

        timeout = int(data.get("timeout", 30))
        llm_response = run_local_llm(prompt, timeout=timeout)
        if "ERROR_TIMEOUT" in llm_response or "ERROR" in llm_response:
            return jsonify({"status": "❌ LLM backend failed or timed out", "result": ""}), 500

        debug_log(f"[parse_script_to_steps] 🔍 LLM raw response:\n{llm_response}")
        debug_log("[parse_script_to_steps] Exited")

        try:
            steps_data = sanitize_llm_json(llm_response)
            step_list = steps_data if isinstance(steps_data, list) else steps_data.get("steps", [])
        except Exception as e:
            debug_log(f"[parse_script_to_steps] ❌ Failed to parse steps JSON: {e}")
            debug_log(f"[parse_script_to_steps] 💕 Raw response was: {llm_response}")
            step_list = []

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rewritten = rewrite_steps(step_list, username, password)

        def inject_navigation_helpers(step):
            if not isinstance(step, dict) or "selector" not in step:
                debug_log("⚠️ inject_navigation_helpers received malformed step")
                return []
            return [
                {"action": "wait_for_selector", "selector": step["selector"], "value": "visible"},
                {"action": "scroll_into_view", "selector": step["selector"]},
                step,
                {"action": "screenshot", "value": None},
                {"action": "log_result", "value": None},
            ]

        click_steps = [s for s in rewritten if isinstance(s, dict) and s.get("action") == "click"]
        target_label, parent_label = None, None
        for i in range(len(click_steps) - 1, -1, -1):
            if click_steps[i].get("label"):
                target_label = click_steps[i]["label"]
                if i > 0 and click_steps[i-1].get("label"):
                    parent_label = click_steps[i-1]["label"]
                break

        if not target_label:
            debug_log("❌ Aborting: No valid click label in steps — cannot determine target for JSONL nav")
            return jsonify({"error": "No target label found — aborting instead of falling back to LLM nav"}), 500

        debug_log(f"🧭 target_label resolved to: {target_label}")
        debug_log(f"🧭 parent_label resolved to: {parent_label}")

        base_steps = []
        try:
            jsonl_path = Path(__file__).resolve().parent.parent / "oracle_ui_dump.jsonl"
            nav_map = load_ui_map(str(jsonl_path))
            debug_log("🧭 UI map loaded — sample entries:")
            for entry in list(nav_map)[:10]:
                if isinstance(entry, dict):
                    debug_log(f"- label='{entry.get('label')}' parent='{entry.get('parent')}' page_id='{entry.get('page_id')}'")
                elif isinstance(entry, (list, tuple)) and len(entry) >= 3:
                    debug_log(f"- label='{entry[0]}' parent='{entry[1]}' page_id='{entry[2]}'")
                else:
                    debug_log(f"- Unrecognized entry format: {entry}")

            page = find_page_id_by_label(nav_map, target_label, parent_label, require_actionable=True)
            if not isinstance(page, dict):
                raise TypeError(f"Invalid page object format from sitemap: {page}")
            page_id = page.get("page_id")
            if not page_id:
                raise ValueError("Missing page_id in resolved page — aborting")

            debug_log(f"🧭 Target page_id resolved to: {page_id}")

            path = resolve_navigation_path(nav_map, page_id)
            debug_log(f"🧭 Navigation path resolved with {len(path)} steps")
            for p in path:
                base_steps.extend(inject_navigation_helpers({
                    "action": p["action_type"],
                    "selector": p["selector"],
                    "value": p.get("value")
                }))
            debug_log("🧭 Using JSONL navigation — skipping LLM-generated steps")

        except Exception as e:
            debug_log(f"⚠️ Navigation error: {type(e).__name__}: {e}")
            debug_log("⚠️ Proceeding to login and run browser without JSONL navigation")

        result = await run_browser_script(
            steps=base_steps,
            session_id=data.get("session_id"),
            login_url=login_url,
            username=username,
            password=password,
            preview_mode=data.get("preview_only", False),
            target_label=target_label,
            parent_label=parent_label,
        )
        debug_log("Exited")
        return jsonify({"status": "✅ Executed", "result": result})

    except Exception as e:
        debug_log(f"run_test_script ❌ Unexpected error: {e}")
        return jsonify({"error": f"Unexpected server error: {e}"}), 500
