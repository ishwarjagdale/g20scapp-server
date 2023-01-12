import datetime
from os import environ
FLASK_ENV = environ.get("FLASK_ENV")
SQLALCHEMY_DATABASE_URI = 'postgresql://scapp:password@localhost:5432/scapp'
FLASK_DEBUG = environ.get("FLASK_DEBUG") or False
SECRET_KEY = environ.get("SECRET_KEY")
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=30)
REMEMBER_COOKIE_SAMESITE = "None"
REMEMBER_COOKIE_HTTPONLY = True
REMEMBER_COOKIE_SECURE = True
