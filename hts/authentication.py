from flask_login import LoginManager

from .database.models.user import User

login_manager = LoginManager()
login_manager.login_view = 'main.index'
login_manager.session_protection = "strong"


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)
