import os
from pathlib import Path
import secrets
from flask import Flask
from .models import close_db, db, SCHEMA

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY') or secrets.token_hex(32), DATABASE=os.environ.get('DATABASE_PATH',str(Path(app.instance_path)/'woodmetrics.sqlite')), SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax', SESSION_COOKIE_SECURE=os.environ.get('COOKIE_SECURE')=='1', MAX_CONTENT_LENGTH=65536)
    if test_config: app.config.update(test_config)
    Path(app.config['DATABASE']).parent.mkdir(parents=True,exist_ok=True)
    app.teardown_appcontext(close_db)
    with app.app_context(): db().executescript(SCHEMA)
    from .controllers import bp
    app.register_blueprint(bp)
    from .seed import register_commands
    register_commands(app)
    return app
