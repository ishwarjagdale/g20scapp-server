import datetime
from os import environ
FLASK_ENV = environ.get("FLASK_ENV")
SQLALCHEMY_DATABASE_URI = 'postgresql://scapp:password@localhost:5432/scapp'
# SQLALCHEMY_DATABASE_URI =
# 'postgresql://roflqvnohnziil:d4a10383c52883ababaaf29570153a1594db0b79fc0471156d9112a00e103f3b@ec2-35-170-21-76
# .compute-1.amazonaws.com:5432/d70oqtafiofkov'
FLASK_DEBUG = environ.get("FLASK_DEBUG") or False
SECRET_KEY = environ.get("SECRET_KEY")
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=30)
REMEMBER_COOKIE_SAMESITE = "None"
REMEMBER_COOKIE_HTTPONLY = True
REMEMBER_COOKIE_SECURE = True
