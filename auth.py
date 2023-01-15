from flask import Blueprint, request, jsonify
from flask_login import LoginManager, login_required, login_user, current_user, logout_user

from database import Users

auth = Blueprint('auth', __name__, url_prefix='/auth', )

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return Users.get_user(user_id=user_id)


@auth.route('/', methods=["GET"])
@login_required
def is_secure():
    return jsonify(current_user.to_dict())


@auth.route('/login', methods=["POST"])
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if email and password:
        user = Users.get_user(email=email)
        if user:
            if user.check_password(password):
                if login_user(user):
                    return jsonify(user.to_dict())
                return jsonify({"message": "something went wrong while logging in"}), 500
            return {"message": "invalid credentials"}, 403
        return jsonify({"message": "user not found"}), 404
    return jsonify({"message": "invalid or missing parameters"}), 400


# @auth.route('/signup', methods=["POST"])
# def signup():
#     name = request.json.get('name', None)
#     email = request.json.get('email', None)
#     password = request.json.get('password', None)
#
#     if name and email and password:
#         user = Users.get_user(email=email)
#         if not user:
#             d_now = datetime.datetime.now(datetime.timezone.utc).timestamp()
#             user = Users(name=name, email_addr=email, date_created=d_now, password=hashlib.sha256(
#                 bytes(str(d_now).replace('.', password), encoding='utf-8')
#             ).hexdigest(), authenticate=True)
#             db.session.add(user)
#             db.session.commit()
#             return jsonify(user.to_dict())
#         return jsonify({"message": "user exists"}), 400
#     return jsonify({"message": "invalid or missing parameters"}), 400


@auth.route('/logout', methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify(200)
