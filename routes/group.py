from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from iam.library.iam_jwt_user import IamJwtUser
from iam.library.validate import validate_group_name, DataValidationError
from iam.models import db, Group, Permission


create_group_route = Blueprint('create_group', __name__)
delete_group_route = Blueprint('delete_group', __name__)
get_groups_route = Blueprint('get_groups', __name__)
get_group_route = Blueprint('get_group', __name__)
edit_group_route = Blueprint('edit_group', __name__)


@create_group_route.route('/api/iam/group', methods=['POST'])
@jwt_required()
def create_group():
    user = IamJwtUser()
    if not user.has_rights('iam_group_manage'):
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


@delete_group_route.route('/api/iam/group/<id>', methods=['DELETE'])
@jwt_required()
def delete_group(id: str):
    user = IamJwtUser()
    id = str(id)
    if not user.has_rights('iam_group_manage'):
        return jsonify({'error': f"User {user.identity['username']} doesn't have rights to delete groups."})

    group = Group.query.get(id)
    if group is None:
        return {'error': 'Group not found.'}, 404

    db.session.delete(group)
    db.session.commit()
    return jsonify({'error': None})


@get_groups_route.route('/api/iam/group', methods=['GET'])
@jwt_required()
def get_groups():
    user = IamJwtUser()
    if not user.has_rights('iam_group_manage'):
        return jsonify({'error': f"User {user.identity['username']} doesn't have rights to list groups."})

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    search = request.args.get('search', None)
    if search is not None and search != '':
        groups = Group.query.filter(Group.name.like(f'%{search}%')).paginate(page=page, per_page=10)
    else:
        groups = Group.query.paginate(page=page, per_page=10)

    return jsonify({
        'error': None,
        'data': [g.short for g in groups.items],
        'pages': groups.pages,
        'page': groups.page
    })


@get_group_route.route('/api/iam/group/<id>', methods=['GET'])
@jwt_required()
def get_group(id: str):
    user = IamJwtUser()
    id = str(id)

    if not user.has_rights('iam_group_manage'):
        return jsonify({'error': f"User {user.identity['username']} doesn't have rights to get groups."})

    group = Group.query.get(id)

    if group is None:
        return {'error': 'Group not found.'}, 404

    return jsonify({'error': None, 'data': group.full})


@edit_group_route.route('/api/iam/group/<id>', methods=['PUT'])
@jwt_required()
def edit_group(id: str):
    user = IamJwtUser()
    id = str(id)

    if not user.has_rights('iam_group_manage'):
        return jsonify({'error': f"User {user.identity['username']} doesn't have rights to edit groups."})

    group = Group.query.get(id)

    if group is None:
        return {'error': 'Group not found.'}, 404

    try:
        name = request.json.get('name', None)
        permissions = request.json.get('permissions', None)

        if name is not None:
            validate_group_name(name)
            name = str(name)
            group.name = name

        if permissions is not None:
            permissions = list(permissions)
            group.permissions = Permission.query.filter(Permission.name.in_(permissions)).all()

        db.session.commit()

        return jsonify({'error': None})

    except (DataValidationError, ValueError) as e:
        if type(e) == 'ValueError':
            return jsonify({'error': 'Wrong input data'})
        return jsonify(e.response), e.code
