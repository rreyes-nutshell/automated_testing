import os
import importlib
from flask import Blueprint
from utils.logging import debug_log


def register_blueprints(app):
    """Auto-discover and register all blueprints in routes/ and providers/."""
    debug_log("Entered")

    for base_folder in ["routes", "providers", "oracle", "sap"]:
        folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', base_folder))
        if not os.path.isdir(folder_path):
            continue

        for root, dirs, files in os.walk(folder_path):
            for filename in files:
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
                                    app.register_blueprint(item)
                                    print(f"✅ Registered blueprint: {item.name}")
                                    break

                    except Exception as e:
                        print(f"⚠️ Failed to load {module_name}: {e}")

    debug_log("Exited")
