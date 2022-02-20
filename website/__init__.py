from flask import Flask
from os import path
from flask_login import LoginManager
from website.user import User
from replit import db
from website.misc import UPLOAD_PATH

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'abcdefghijklmnopqrstuvwxyz'
    app.config["UPLOAD_FOLDER"] = UPLOAD_PATH
    from .views import views
    from .auth import auth
  
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    #sets up login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    #Communicates with flask how we load a user
    @login_manager.user_loader
    def load_user(id):
        return User(id)
      
    return app

