import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = os.urandom(32)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or SECRET_KEY
    SQLALCHEMY_DATABASE_URI = (
            os.environ.get('DATABASE_URL') or
            'sqlite:///' + os.path.join(BASE_DIR, 'todo.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


config = Config()