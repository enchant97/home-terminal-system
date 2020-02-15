__version__ = "2.0.0"

from flask import Flask, render_template
from os import getenv

from .authentication import login_manager
from .config import config
from .models import db
from .views import account, home, hwm, main, pd1, fm4

app = Flask(__name__)

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

def create_app():
    """
    Creates the app and configures SQLALCHEMY

    returns:
        Flask app
    """
    config_name = getenv("FLASK_CONFIGURATION", "dev")
    app.config.from_object(config[config_name])
    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(account)
    app.register_blueprint(home, url_prefix="/home")
    app.register_blueprint(hwm, url_prefix="/hwm")
    app.register_blueprint(fm4, url_prefix="/fm4")
    app.register_blueprint(pd1, url_prefix="/pd1")

    with app.app_context():
        db.create_all()
    return app
