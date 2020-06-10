"""
python app built with flask designed to digitize
certain tasks that can be done around the home

to use import create_app() which returns an flask app for running
"""

__version__ = "3.6.6"
__author__ = "Leo Spratt"

import os
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template
from flask_login import current_user
from werkzeug.utils import find_modules, import_string

from .authentication import login_manager
from .config import config
from .database.dao.user import get_notifations, new_account
from .database.database import db
from .views import account, api, fm, home, hwm, im, main, pm, reminder

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

def get_plugins():
    """
    imports the plugins and registers the blueprints,

    yields:
        dir name,
        PluginData
    """
    plugins_dir = Path(__file__).resolve(strict=True).parent / "plugins"
    for path in plugins_dir.iterdir():
        folder_name = path.name
        if path.is_dir() and folder_name != "__pycache__":
            plugin = import_string(f"HomeTerminal.plugins.{folder_name}")
            if hasattr(plugin, "blueprint"):
                if hasattr(plugin, "PluginData"):
                    app.register_blueprint(plugin.blueprint)
                    yield folder_name, plugin.PluginData # yield the plugin name and its setup data
                    app.logger.debug(f"loaded plugin: {plugin.blueprint.name}")
                else:
                    app.logger.error(f"could not load plugin {path} as load_plugin() could not be found")
            else:
                app.logger.error(f"could not load plugin {path} as blueprint could not be found")

def load_plugins():
    """
    Run once inside create_app(), this registers the plugins for use,
    also imports the models if they have any so is run for db.create_all()
    """
    version_now = __version__.split(".")
    for plugin in get_plugins():
        # check if plugin is compatable
        if plugin[1].written_for_version.split(".")[0] == version_now[0]:
            if plugin[1].has_models:
                # import the models if the plugin has indicated they have any
                models_dir = Path(__file__).resolve(strict=True).parent / "plugins" / plugin[0] / "models"
                import_path = f"HomeTerminal.plugins.{plugin[0]}.models"
                import_models(models_dir, import_path)
            # store the PluginData in app.config for potential use within app
            app.config["LOADED_PLUGINS"] = {plugin[1].unique_name : plugin[1]}
        else:
            app.logger.error(f"plugin {plugin[0]} incompatable as is version {plugin[1].written_for_version}")

def import_models(models_dir, import_path):
    """
    used to import all database models found in given directory,
    can be run several times if there are different model directories

    args:
        models_dir : the directory where db models are located
        import_path : the import path for the models directory

    example:
        models_dir : path to models
        import_path :  HomeTerminal.database.models
    """
    # Source: https://gist.github.com/languanghao/a24d74b8ab4232a801312e2a0a107064
    # Source: https://github.com/davidism/basic_flask
    for py in [f[:-3] for f in os.listdir(models_dir) if f.endswith('.py') and f != '__init__.py']:
        mod = __import__('.'.join([import_path, py]), fromlist=[py])
        classes = [getattr(mod, x) for x in dir(mod) if isinstance(getattr(mod, x), type)]
        for cls in classes:
            if 'flask_sqlalchemy.' in str(type(cls)):
                app.logger.debug("auto import db model: {0}".format(cls))
                setattr(sys.modules[__name__], cls.__name__, cls)

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
    app.register_blueprint(im, url_prefix="/inventory-manager")
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(reminder, url_prefix="/reminder")

    # import database models from the apps model folder
    models_dir = Path(__file__).resolve(strict=True).parent / "database" / "models"
    import_path = "HomeTerminal.database.models"
    import_models(models_dir, import_path)

    # import plugins or not
    if app.config.get("ENABLE_PLUGINS", True):
        app.logger.info("loading plugins...")
        load_plugins()
        app.logger.info("finished loading plugins")
    else:
        app.logger.info("not loading plugins as it is disabled in config")

    with app.app_context():
        db.create_all()

    return app
