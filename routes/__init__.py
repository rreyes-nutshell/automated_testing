import os
import importlib
from flask import Blueprint
from utils.logging import debug_log


def register_blueprints(app):
    # """Auto-discover and register all blueprints in routes/, providers/, oracle/, and sap/."""
    debug_log("Entered")

    for base_folder in ["routes", "providers", "oracle", "sap"]:
    #"""Auto-discover and register all blueprints in common folders."""

        debug_log("Entered")

        search_folders = ["routes", "providers", "oracle", "sap"]
        for base_folder in search_folders:
            folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', base_folder))
            if not os.path.isdir(folder_path):
                continue
            debug_log(f"Scanning {folder_path}")

            for root, dirs, files in os.walk(folder_path):
                for filename in files:
                    if filename.endswith("web_ui.py"):
                        continue
                    if filename.endswith(".py") and filename != "__init__.py":
                        module_path = os.path.relpath(os.path.join(root, filename), os.path.dirname(__file__) + '/..')
                        module_name = module_path.replace("/", ".").replace("\\", ".").replace(".py", "")

                        try:
                            module = importlib.import_module(module_name)

                            # Only register Blueprint instances whose variable name ends with _bp
                            for item_name in dir(module):
                                if item_name.endswith("_bp"):
                                    item = getattr(module, item_name)
                                    if isinstance(item, Blueprint):
                                        if item.name in app.blueprints:
                                            debug_log(f"Skipping already registered blueprint: {item.name}")
                                            continue
                                        app.register_blueprint(item)
                                        print(f"✅ Registered blueprint: {item.name}")
                                        break

                        except Exception as e:
                            print(f"⚠️ Failed to load {module_name}: {e}")

    debug_log("Exited")
