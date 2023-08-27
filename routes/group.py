from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from iam.library.iam_jwt_user import IamJwtUser
from iam.library.validate import validate_group_name, DataValidationError
from iam.models import db, Group


create_group_route = Blueprint('create_group', __name__)
delete_group_route = Blueprint('delete_group', __name__)
get_groups_route = Blueprint('get_groups', __name__)
get_group_route = Blueprint('get_group', __name__)
edit_group_route = Blueprint('edit_group', __name__)


@create_group_route.route('/api/iam/group', methods=[])
@jwt_required()
def create_group():
    user = IamJwtUser()
    if not user.has_rights('iam_create_group'):
        return jsonify({'error': f"User {user.identity['username']} doesn't have rights to create groups."})
    name = str(request.json.get('name', None))
    try:
        validate_group_name(name)
    except DataValidationError as e:
        return jsonify(e.response), e.code
    group = Group(name=name)
    db.session.add(group)
    db.session.commit()
    return jsonify({'error': None})



@delete_group_route.route('/api/iam/group/<id>', methods=[])
@jwt_required()
def delete_group(id: str):
    pass


@get_groups_route.route('/api/iam/group', methods=[])
@jwt_required()
def get_groups():
    pass


@get_group_route.route('/api/iam/group/<id>', methods=[])
@jwt_required()
def get_group(id: str):
    pass


@edit_group_route.route('/api/iam/group/<id>', methods=[])
@jwt_required()
def edit_group(id: str):
    pass
