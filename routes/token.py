from flask import Blueprint, jsonify, abort, request
from iam.models import User
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token
from iam.library.iam_jwt_user import IamJwtUser

get_token_route = Blueprint("get_token", __name__)
refresh_token_route = Blueprint("refresh_token", __name__)


@get_token_route.route('/api/iam/token', methods=['POST'])
def get_token():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify({"error": "Bad username or password"}), 401
    if not user.check_pass(password):
        return jsonify({"error": "Bad username or password"}), 401

    return jsonify({
        "error": None,
        "access_token": create_access_token(identity=user.identity),
        "refresh_token": create_refresh_token(identity=user.identity)
    })


@refresh_token_route.route('/api/iam/token', methods=['GET'])
@jwt_required
def refresh_token():
    user_token = IamJwtUser()
    user = user_token.get_db_obj()
    return jsonify({
        "error": None,
        "token": create_access_token(identity=user.identity)
    })

