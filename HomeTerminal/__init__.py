__version__ = "2.0.0"

from datetime import datetime
from os import getenv

from flask import Flask, render_template

from .authentication import login_manager
from .config import config
from .dao import new_account
from .models import db
from .views import account, api, fm4, home, hwm, main, pd1

app = Flask(__name__)

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.before_first_request
def create_default_db():
    """
    Creates the default rows in the database,
    runs before_first_request
    """
    new_account(app.config["ADMINUSERNAME"], app.config["ADMINUSERNAME"], datetime.utcnow(), ignore_duplicate=True)

def create_app():
    """
    Creates the app and configures SQLALCHEMY

    returns:
        Flask app
    """
    config_name = getenv("FLASK_CONFIGURATION", "dev")
    app.config.from_object(config[config_name])
    app.config["APP_VERSION"] = __version__
    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(account)
    app.register_blueprint(home, url_prefix="/home")
    app.register_blueprint(hwm, url_prefix="/hwm")
    app.register_blueprint(fm4, url_prefix="/fm4")
    app.register_blueprint(pd1, url_prefix="/pd1")
    app.register_blueprint(api, url_prefix="/api")

    with app.app_context():
        db.create_all()
    return app
