<<<<<<< HEAD
import os
from flask import Flask, render_template
from routes import register_blueprints
from utils.logging import debug_log
from dotenv import load_dotenv


# Load .env from instance/ folder
base_dir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(base_dir, "instance", ".env")
if not os.path.exists(env_path):
	env_path = os.path.join(base_dir, "..", "instance", ".env")
load_dotenv(env_path)

=======
import sys
import os
from dotenv import load_dotenv
from flask import Flask
from routes import register_blueprints
from utils.logging import debug_log

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

load_dotenv()
>>>>>>> 61b9b8f (Patch UI Mapper: crawler, extractor, schema updates, HTML fixes)

def create_app():
	app = Flask(__name__, instance_relative_config=True)
	app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback_secret_key")
	register_blueprints(app)

	print("✅ Registered Flask Endpoints:")
	for rule in app.url_map.iter_rules():
		print(rule.endpoint, rule)
<<<<<<< HEAD

	debug_log("✅ Flask app created")
=======
>>>>>>> 61b9b8f (Patch UI Mapper: crawler, extractor, schema updates, HTML fixes)
	return app

if __name__ == "__main__":
	app = create_app()
<<<<<<< HEAD
	app.run(debug=True)
=======
	app.run(debug=True, host="0.0.0.0")
>>>>>>> 61b9b8f (Patch UI Mapper: crawler, extractor, schema updates, HTML fixes)
