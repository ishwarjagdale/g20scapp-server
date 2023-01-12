from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from flask import current_app
import hashlib


db = SQLAlchemy()


class Users(db.Model):
    __table_name__ = "users"

    user_id = db.Column(db.INTEGER, primary_key=True)
    email_addr = db.Column(db.VARCHAR, unique=True, nullable=False)
    password = db.Column(db.VARCHAR, nullable=False)
    name = db.Column(db.VARCHAR, default="anonymous", nullable=False)
    date_created = db.Column(db.VARCHAR, default=datetime.now(timezone.utc).timestamp(), nullable=False)
    authenticated = db.Column(db.BOOLEAN, default=False, nullable=False)

    @property
    def is_active(self):
        return self.authenticated

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.user_id)

    def __eq__(self, other):
        if isinstance(other, Users):
            return self.get_id() == other.get_id()

    def __ne__(self, other):
        return not self.__eq__(other)

    @staticmethod
    def get_user(email=None, user_id=None):
        if email:
            return Users.query.filter_by(email_addr=email).first()
        if user_id:
            return Users.query.filter_by(user_id=user_id).first()
        return False

    def check_password(self, password):
        print(hashlib.sha256(bytes(str(self.date_created).replace(".", password), encoding='utf-8')). \
                   hexdigest())
        print(self.password)
        return hashlib.sha256(bytes(str(self.date_created).replace(".", password), encoding='utf-8')). \
                   hexdigest() == self.password

    def generate_token(self):
        return hashlib.sha256(bytes(
            f"{current_app.config['SECRET_KEY']}.{self.email_addr}.{datetime.now().timestamp()}",
            encoding='utf-8')
        ).hexdigest()

    def authenticate(self):
        try:
            self.authenticated = True
            db.session.commit()
        except Exception as e:
            print(e)
            return False
        return self.authenticated

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email_addr
        }


class Monuments(db.Model):
    __table_name__ = "monuments"

    monument_id = db.Column(db.VARCHAR, primary_key=True)
    name = db.Column(db.VARCHAR, nullable=False)
    long = db.Column(db.VARCHAR)
    lat = db.Column(db.VARCHAR)
    views = db.Column(db.Integer, default=0, nullable=False)
    category = db.Column(db.VARCHAR, nullable=False)


class MonumentImages(db.Model):
    __table_name__ = "monumentImages"

    monument_id = db.Column(db.VARCHAR, db.ForeignKey('monuments.monument_id', ondelete="CASCADE"), nullable=False)
    image = db.Column(db.VARCHAR, nullable=False)

    p_key = db.PrimaryKeyConstraint(monument_id, image)


class MonumentTranslations(db.Model):
    __table_name__ = "monumentTranslations"

    monument_id = db.Column(db.VARCHAR, db.ForeignKey('monuments.monument_id', ondelete="CASCADE"), nullable=False)
    language_code = db.Column(db.VARCHAR, nullable=False)
    name = db.Column(db.VARCHAR, nullable=False)
    description = db.Column(db.VARCHAR, nullable=False)
    audio = db.Column(db.VARCHAR)

    p_key = db.PrimaryKeyConstraint(monument_id, language_code)
