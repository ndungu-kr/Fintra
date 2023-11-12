from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path, pardir, makedirs, getenv
from flask_login import LoginManager
from dotenv import load_dotenv


load_dotenv()


db = SQLAlchemy()


# Get the parent directory path
parent_dir = path.abspath(path.join(path.dirname(__file__), pardir))

# Set the path for the database file within the 'Database' folder in the parent directory
DB_FOLDER = path.join(parent_dir, 'Database')
makedirs(DB_FOLDER, exist_ok=True)  # Create 'Database' folder if it doesn't exist

DB_NAME = path.join(DB_FOLDER, 'database.db')


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = getenv('DB_SECRET_KEY')
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User

    with app.app_context():
        db.create_all()
        print("Database running...")

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
