from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO
from .config import Config

db            = SQLAlchemy()
bcrypt        = Bcrypt()
login_manager = LoginManager()
socketio      = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    login_manager.login_view = 'main.login'

    from .routes import main
    app.register_blueprint(main)

    from . import sockets

    with app.app_context():
        db.create_all()

    return app
