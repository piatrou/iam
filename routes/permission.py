from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from iam.library.iam_jwt_user import IamJwtUser
from iam.library.validate import validate_permission_name, DataValidationError
from iam.models import db, Group, Permission


create_permission_route = Blueprint('create_permission', __name__)
delete_permission_route = Blueprint('delete_permission', __name__)
get_permissions_route = Blueprint('get_permissions', __name__)
get_permission_route = Blueprint('get_permission', __name__)
edit_permission_route = Blueprint('edit_permission', __name__)


@create_permission_route.route('/api/iam/permission', methods=['POST'])
@jwt_required()
def create_permission():
    user = IamJwtUser()
    if not user.has_rights('iam_permission_manage'):
        return jsonify({'error': f"User {user.identity['username']} doesn't have rights to create permissions."})
    name = str(request.json.get('name', None))
    description = str(request.json.get('description', None))
    try:
        validate_permission_name(name)
    except DataValidationError as e:
        return jsonify(e.response), e.code
    permission = Permission(name=name, description=description)
    db.session.add(permission)
    db.session.commit()
    return jsonify({'error': None})


@delete_permission_route.route('/api/iam/permission/<id>', methods=['DELETE'])
@jwt_required()
def delete_permission(id: str):
    user = IamJwtUser()
    id = str(id)
    if not user.has_rights('iam_permission_manage'):
        return jsonify({'error': f"User {user.identity['username']} doesn't have rights to delete permissions."})

    permission = Permission.query.get(id)
    if permission is None:
        return {'error': 'Permission not found.'}, 404

    db.session.delete(permission)
    db.session.commit()
    return jsonify({'error': None})


@get_permissions_route.route('/api/iam/permission/', methods=['GET'])
@jwt_required()
def get_permissions():
    user = IamJwtUser()
    if not user.has_rights('iam_permission_manage'):
        return jsonify({'error': f"User {user.identity['username']} doesn't have rights to list permissions."})

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    search = request.args.get('search', None)
    if search is not None and search != '':
        permission = Permission.query.filter(Permission.name.like(f'%{search}%')).paginate(page=page, per_page=10)
    else:
        permission = Permission.query.paginate(page=page, per_page=10)

    return jsonify({
        'error': None,
        'data': [p.short for p in permission.items],
        'pages': permission.pages,
        'page': permission.page
    })


@get_permission_route.route('/api/iam/permission/<id>', methods=['GET'])
@jwt_required()
def get_permission(id: str):
    user = IamJwtUser()
    id = str(id)

    if not user.has_rights('iam_permission_manage'):
        return jsonify({'error': f"User {user.identity['username']} doesn't have rights to get permissions."})

    permission = Permission.query.get(id)

    if permission is None:
        return {'error': 'Permission not found.'}, 404

    return jsonify({'error': None, 'data': permission.full})


@edit_permission_route.route('/api/iam/permission/<id>', methods=['PUT'])
@jwt_required()
def edit_permission(id: str):
    user = IamJwtUser()
    id = str(id)

    if not user.has_rights('iam_permission_manage'):
        return jsonify({'error': f"User {user.identity['username']} doesn't have rights to edit permissions."})

    permission = Permission.query.get(id)

    if permission is None:
        return {'error': 'Permission not found.'}, 404

    try:
        name = request.json.get('name', None)
        description = request.json.get('description', None)

        if name is not None:
            validate_permission_name(name)
            name = str(name)
            permission.name = name

        if description is not None:
            description = str(description)
            permission.description = description

        db.session.commit()

        return jsonify({'error': None})

    except (DataValidationError, ValueError) as e:
        if type(e) == 'ValueError':
            return jsonify({'error': 'Wrong input data'})
        return jsonify(e.response), e.code







