import os
import importlib
from flask import Blueprint

def register_blueprints(app):
<<<<<<< HEAD
    for base_folder in ["oracle", "sap", "routes", "providers"]:
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
                        for item_name in dir(module):
                            if item_name.endswith("_bp"):
                                item = getattr(module, item_name)
                                if isinstance(item, Blueprint):
                                    app.register_blueprint(item)
                                    print(f"✅ Registered blueprint: {item.name}")
                                    break
                    except Exception as e:
                        print(f"⚠️ Failed to load {module_name}: {e}")
=======
	"""Auto-discover and register all blueprints in routes/ and providers/."""
	for base_folder in ["routes", "providers", "oracle"]:
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
						for item_name in dir(module):
							if item_name.endswith("_bp"):
								item = getattr(module, item_name)
								if isinstance(item, Blueprint):
									app.register_blueprint(item)
									print(f"✅ Registered blueprint: {item.name}")
									break
					except Exception as e:
						print(f"⚠️ Failed to load {module_name}: {e}")

	# Manual patch removed: ui_map_viewer now autoloads from oracle/ui_mapper/
>>>>>>> 61b9b8f (Patch UI Mapper: crawler, extractor, schema updates, HTML fixes)
