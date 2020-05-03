__version__ = "3.4.4"

import logging
import os
import sys
from datetime import datetime

from flask import Flask, render_template
from flask_login import current_user

from .authentication import login_manager
from .config import config
from .database.dao.user import get_notifations, new_account
from .database.database import db
from .views import (account, api, fm, home, hwm, main,
                    pm, reminder)

app = Flask(__name__)

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

# source: https://stackoverflow.com/questions/6036082/call-a-python-function-from-jinja2
@app.context_processor
def notif_context():
    def get_jinja_notifications():
        return get_notifations(current_user.username)
    return dict(get_jinja_notifications=get_jinja_notifications)

@app.before_first_request
def create_default_db():
    """
    Creates the default rows in the database,
    runs before_first_request
    """
    new_account(
        app.config["ADMINUSERNAME"], app.config["ADMINUSERNAME"],
        datetime.utcnow(), ignore_duplicate=True)

def create_app():
    """
    Creates the app and configures SQLALCHEMY

    returns:
        Flask app
    """
    config_name = os.getenv("FLASK_CONFIGURATION", "dev")
    app.config.from_object(config[config_name])
    app.config["APP_VERSION"] = __version__
    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(account)
    app.register_blueprint(home, url_prefix="/home")
    app.register_blueprint(hwm, url_prefix="/homework-manager")
    app.register_blueprint(fm, url_prefix="/freezer-manager")
    app.register_blueprint(pm, url_prefix="/photo-manager")
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(reminder, url_prefix="/reminder")

    with app.app_context():
        # Source: https://gist.github.com/languanghao/a24d74b8ab4232a801312e2a0a107064
        # Source: https://github.com/davidism/basic_flask
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "models")
        for py in [f[:-3] for f in os.listdir(path) if f.endswith('.py') and f != '__init__.py']:
            mod = __import__('.'.join(['HomeTerminal.database.models', py]), fromlist=[py])
            classes = [getattr(mod, x) for x in dir(mod) if isinstance(getattr(mod, x), type)]
            for cls in classes:
                if 'flask_sqlalchemy.' in str(type(cls)):
                    logging.debug("auto import db model: {0}".format(cls))
                    setattr(sys.modules[__name__], cls.__name__, cls)
        db.create_all()
    return app
