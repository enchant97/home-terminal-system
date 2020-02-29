from flask_login import LoginManager

from .models import User

login_manager = LoginManager()
login_manager.login_view = 'main.index'

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)
