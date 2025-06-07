from utils.logging import debug_log, log_step_to_file
from datetime import datetime
from utils.selectors import ensure_escaped_selector
import re

NAV_LINKS = [
    "Scheduled Processes",
    "Show More",
    "Tools",
    "Home",
    "Reports and Analytics",
    "Financial Reporting Center"
]

def build_login_steps(username, password):
    return [
        {"action": "wait_for_selector", "selector": "input[name='userid']"},
        {"action": "fill",             "selector": "input[name='userid']", "value": username},
        {"action": "fill",             "selector": "input[name='password']", "value": password},
        {"action": "wait_for_selector", "selector": "button#btnActive"},
        {"action": "evaluate_click",    "selector": "button#btnActive"},
        {"action": "wait_for_timeout",  "value": "3000"},
        {"action": "wait_for_url",      "value": "https://.*oraclecloud.com/.*Welcome.*"},
        {"action": "wait_for_selector", "selector": "text='Sign Out'"},
    ]

def rewrite_steps(steps, username=None, password=None, session_id=None):
    """
    Accept either:
      • A flat list of step‐dicts (old behavior), or
      • A list of test‐case objects, each with "test_name" and a "steps" array.
    In the latter case, rewrite each sub‐step using existing logic, then preserve the test‐case structure.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    debug_log("Entered rewrite_steps")

    def _rewrite_flat_steps(flat_steps):
        rewritten_flat = []
        login_inserted = False
        show_more_injected = False
        current_section = None

        for step in flat_steps:
            orig_selector = step.get("selector") or ""
            orig_action   = step.get("action", "")
            value         = step.get("value", "")

            # 1) Handle any “Select All” / unchecked‐checkbox patterns:
            #    - orig_selector.startswith(".checkbox:not")
            #    - "selectall" in lowercase
            #    - "#select-all" in the selector (e.g. "#select-all-checkbox")
            #    - OR any css:… containing "checkbox"
            lower_sel = orig_selector.lower().replace(" ", "")
            if orig_action == "click" and (
                   orig_selector.startswith(".checkbox:not")
                or "selectall" in lower_sel
                or ("select-all" in lower_sel)
                or "checkbox" in lower_sel
            ):
                
                if orig_selector.startswith(".checkbox:not"):
                    context_label = current_section or ""
                elif "selectall" in lower_sel or "select-all" in lower_sel:
                    # strip off any "#", "selectAll" or "select-all" from the selector to derive context
                    stripped = re.sub(r"#?select[-_]?all[\w-]*", "", orig_selector, flags=re.IGNORECASE)
                    context_label = re.sub(r'(?<=[a-z])(?=[A-Z])', " ", stripped).strip()
                else:
                    context_label = current_section or ""

                # (a) click the “Select All” label via locator().filter({ hasText: /^Select All$/ }).first().click()
                click_label_step = {
                    "action":  "click_locator",
                    "locator": "span.filter({ hasText: /^Select All$/ }).first()",
                    "context": context_label
                }
                debug_log(f"Rewriting into click_locator for 'Select All' span: {click_label_step}")
                rewritten_flat.append(click_label_step)
                log_step_to_file("rewrite", click_label_step, session_id=session_id)

                # (b) check the actual checkbox inside that row
                check_box_step = {
                    "action":  "check_by_role",
                    "role":    "checkbox",
                    "name":    "Select All",
                    "rowName": context_label
                }
                debug_log(f"Rewriting into check_by_role for the checkbox: {check_box_step}")
                rewritten_flat.append(check_box_step)
                log_step_to_file("rewrite", check_box_step, session_id=session_id)
                continue

            # 2) Handle “Export to Excel” icons
            if orig_action == "click" and "export" in orig_selector.lower():
                wait_export = {
                    "action":   "wait_for_selector",
                    "selector": "get_by_role(\"button\", { name: 'Export to Excel' })"
                }
                debug_log(f"Injecting wait_for_selector before export: {wait_export}")
                rewritten_flat.append(wait_export)
                log_step_to_file("rewrite", wait_export, session_id=session_id)

                export_step = {
                    "action":  "click_by_role",
                    "role":    "button",
                    "name":    "Export to Excel",
                    "context": current_section
                }
                debug_log(f"Rewriting export icon step into click_by_role: {export_step}")
                rewritten_flat.append(export_step)
                log_step_to_file("rewrite", export_step, session_id=session_id)
                continue

            # 3) Detect login sequence and inject once
            if not login_inserted and orig_action == "fill" and "userid" in orig_selector:
                debug_log("🔐 Injecting login steps")
                rewritten_flat.extend(build_login_steps(username or "", password or ""))
                login_inserted = True
                continue

            # 4) Rewrite “goto” → “click” if not a full URL
            if orig_action == "goto" and orig_selector and not orig_selector.startswith("http"):
                step["action"] = "click"

            # 5) After “Navigator” click, inject Show More (once)
            if not show_more_injected and orig_action == "click" and "Navigator" in orig_selector:
                debug_log("Injecting Show More steps after Navigator click")
                rewritten_flat.append(step)
                rewritten_flat.append({"action": "wait_for_timeout", "value": "2000"})
                rewritten_flat.append({"action": "log_html",        "value": "after_navigator"})
                rewritten_flat.append({"action": "screenshot",       "value": "after_navigator"})
                rewritten_flat.append({"action": "debug_pause"})
                rewritten_flat.append({
                    "action":   "wait_for_selector",
                    "selector": "get_by_role(\"link\", name=\"Show More\")",
                    "value":    "visible"
                })
                rewritten_flat.append({
                    "action": "click_by_role",
                    "role":   "link",
                    "name":   "Show More"
                })
                rewritten_flat.append({"action": "wait_for_timeout", "value": "1000"})
                show_more_injected = True
                continue

            # 6) Skip redundant “Tools” if Show More done
            if show_more_injected and step.get("name") == "Tools":
                debug_log("⏭️ Skipping redundant Tools step after Show More")
                continue

            # 7) Handle generic CSS selectors starting with “.”
            if orig_action == "click" and orig_selector.startswith("."):
                label_body = orig_selector.lstrip(".")
                label = re.sub(r'(?<=[a-z])(?=[A-Z])', " ", label_body).strip()
                if label.endswith(" Tab"):
                    label = label[:-4].strip()
                current_section = label
                step["context"] = label

                escaped = ensure_escaped_selector(orig_selector)
                wait_step = {
                    "action":   "wait_for_selector",
                    "selector": f"css={escaped}"
                }
                debug_log(f"Injecting wait_for_selector before CSS click: {wait_step}")
                rewritten_flat.append(wait_step)

                debug_log(f"Rewriting step: {step}")
                rewritten_flat.append(step)
                log_step_to_file("rewrite", step, session_id=session_id)
                continue

            # 8) Handle CSS selectors starting with “css=”
            if orig_action == "click" and orig_selector.startswith("css="):
                raw_css = orig_selector.split("=", 1)[1]
                escaped = ensure_escaped_selector(raw_css)
                wait_step = {
                    "action":   "wait_for_selector",
                    "selector": f"css={escaped}"
                }
                debug_log(f"Injecting wait_for_selector before generic CSS click: {wait_step}")
                rewritten_flat.append(wait_step)

                debug_log(f"Rewriting step: {step}")
                rewritten_flat.append(step)
                log_step_to_file("rewrite", step, session_id=session_id)
                continue

            # 9) Handle text= clicks (“text=…”)
            if orig_action == "click" and orig_selector.startswith("text="):
                label = orig_selector.split("=", 1)[1].strip().strip("\"'")
                current_section = label
                step["context"] = label
                wait_step = {
                    "action":   "wait_for_selector",
                    "selector": orig_selector
                }
                debug_log(f"Injecting wait_for_selector before text click: {wait_step}")
                rewritten_flat.append(wait_step)

                debug_log(f"Rewriting step: {step}")
                rewritten_flat.append(step)
                log_step_to_file("rewrite", step, session_id=session_id)
                continue

            # 10) Default: log and append as-is
            debug_log(f"Rewriting step: {step}")
            rewritten_flat.append(step)
            log_step_to_file("rewrite", step, session_id=session_id)

            # Optional pause after Tools click
            if orig_action == "click" and "cl1" in orig_selector:
                rewritten_flat.append({"action": "wait_for_timeout", "value": "2000"})

        # Append final screenshot + result marker
        rewritten_flat.append({"action": "screenshot", "value": f"final_state_{timestamp}"})
        rewritten_flat.append({"action": "log_result",  "value": "✅ Navigation successful"})
        return rewritten_flat

    # Detect if input is a list of test‐case objects
    if (
        isinstance(steps, list)
        and steps
        and all(isinstance(item, dict) and "test_name" in item and isinstance(item.get("steps"), list) for item in steps)
    ):
        rewritten_cases = []
        for case in steps:
            test_name = case.get("test_name")
            substeps  = case.get("steps", [])

            debug_log(f"Rewriting {len(substeps)} steps inside test case '{test_name}'")
            rewritten_substeps = _rewrite_flat_steps(substeps)
            rewritten_cases.append({
                "test_name": test_name,
                "steps":     rewritten_substeps
            })
        debug_log("Exited rewrite_steps")
        return rewritten_cases

    rewritten_flat = _rewrite_flat_steps(steps)
    debug_log("Exited rewrite_steps")
    return rewritten_flat
