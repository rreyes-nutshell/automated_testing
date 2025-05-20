import os
from flask import Flask
from routes import register_blueprints
from utils.logging import debug_log
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), 'instance', '.env'))


def create_app():
    debug_log("Entered")
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback_secret_key")

    # Auto-load all blueprints from routes/
    register_blueprints(app)

    print("✅ Registered Flask Endpoints:")
    for rule in app.url_map.iter_rules():
        print(rule.endpoint, rule)
    debug_log("Exited")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
