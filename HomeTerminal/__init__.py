__version__ = "2.0.0"

from flask import Flask, render_template

from .authentication import login_manager
from .config import Config
from .models import db
from .views import account, home, hwm, main, pd1, fm4

CONFIG = None
app = Flask(__name__)

@app.errorhandler(404)
def not_found(e):
    return render_template("servererror.html", error=e), 404

def create_app(config_file="usersettings.json"):
    """
    Creates the app and configures SQLALCHEMY

    args:
        config_file : where the app config file is stored
    returns:
        Flask app
    """
    global CONFIG
    #TODO: read config in through flask built in reader
    CONFIG = Config(config_file)
    app.config["SERVER_ERROR_MESSAGE"] = CONFIG.get_server_error_message()
    app.config["ADMINUSERNAME"] = CONFIG.get_admin_username()
    app.config["SECRET_KEY"] = CONFIG.get_secretkey()
    app.config["SQLALCHEMY_DATABASE_URI"] = CONFIG.get_db_path()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
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
