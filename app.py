import os

from flask import Flask
from database import db
from auth import auth, login_manager
from api.admin import admin
from api.app import api
from flask_cors import CORS
from share import share

app = Flask(__name__)
app.config.from_pyfile('config.py')
CORS(app, supports_credentials=True)

with app.app_context():
    login_manager.init_app(app)
    db.init_app(app)
    db.create_all()


app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(api)
app.register_blueprint(share)


@app.route('/url_qr')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get("PORT") or 5000)
