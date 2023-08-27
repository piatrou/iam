from flask import Blueprint, jsonify, request
from iam.models import db, User, Group
from flask_jwt_extended import jwt_required
from iam.library.iam_jwt_user import IamJwtUser
from iam.library.validate import validate_password, validate_name, validate_username, DataValidationError

create_user_route = Blueprint("create_user", __name__)
get_users_route = Blueprint("get_users", __name__)
get_user_route = Blueprint("get_user", __name__)
edit_user_route = Blueprint("edit_user", __name__)
delete_user_route = Blueprint("delete_user", __name__)


@create_user_route.route('/api/iam/user', methods=['POST'])
def create_user():
    username = str(request.json.get('username', None))
    password = str(request.json.get('password', None))
    name = str(request.json.get('name', None))
    try:
        validate_username(username)
        validate_password(password)
        validate_name(name)
    except DataValidationError as e:
        return jsonify(e.response), e.code

    if name is None or name == '':
        name = username

    default_group = Group.query.filter_by(name='users').first()

    new_user = User(
        active=False,
        username=username,
        name=name,
        password=password,
        groups=[default_group]
    )

    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        'error': None
    }), 201


@get_users_route.route('/api/iam/user', methods=['GET'])
@jwt_required()
def get_users():
    user = IamJwtUser()

    if not user.has_rights('iam_users_manage'):
        return jsonify({
            'error': f'User {user.identity["username"]} don\'t have permissions to list users'
        }), 403

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    search = request.args.get('search', None)
    if search is not None and search != '':
        users = User.query.filter(User.username.like(f'%{search}%')).paginate(page=page, per_page=10)
    else:
        users = User.query.paginate(page=page, per_page=10)
    return jsonify({
        'error': None,
        'data': [u.short for u in users.items],
        'pages': users.pages,
        'page': users.page
    })


@get_user_route.route('/api/iam/user/<id>', methods=['GET'])
@jwt_required()
def get_user(id: str = 'self'):
    try:
        id = str(id)
    except ValueError:
        id = 'self'
    current_user = IamJwtUser()

    if id == 'self':
        return jsonify(current_user.identity)

    if not current_user.has_rights('iam_users_manage'):
        return jsonify({
            'error': f"User {current_user.identity['username']} doesn't have permissions to view users"
        }), 403

    user = User.query.get(id)

    if user is None:
        return {'error': 'User not found.'}, 404

    return jsonify({'error': None, 'data': user.identity})


@edit_user_route.route('/api/iam/user/<id>', methods=['PUT'])
@jwt_required()
def edit_user(id: str = 'self'):
    try:
        id = str(id)
    except ValueError:
        id = 'self'
    current_user = IamJwtUser()

    if not current_user.has_rights('iam_users_manage') and id != 0:
        return jsonify({
            'error': f"User {current_user.identity['username']} doesn't have permissions to edit users"
        }), 403

    if id == 'self':
        user = current_user.get_db_obj()
    else:
        user = User.query.get(id)

    if user is None:
        return {'error': 'User not found.'}, 404

    try:
        name = request.json.get('name', None)
        password, old_password = request.json.get('password', None), request.json.get('old_password', None)
        groups = request.json.get('groups', None)

        if name is not None:
            name = str(name)
            validate_name(name)
            if name == user.name:
                raise DataValidationError('Name not changed')
            user.name = name

        if password is not None:
            password, old_password = str(password), str(old_password)
            if not user.check_pass(old_password) and not current_user.has_rights('iam_users_manage'):
                raise DataValidationError('Old password is not correct')
            validate_password(password)
            user.password = password

        if groups is not None:
            groups = list(groups)
            if not current_user.has_rights('iam_users_manage'):
                raise DataValidationError("User doesn't have permissions to edit group list", 403)
            user.groups = Group.query.filter(Group.name.in_(groups)).all()
        db.session.commit()

        return jsonify({'error': None})

    except (DataValidationError, ValueError) as e:
        if type(e) == 'ValueError':
            return jsonify({'error': 'Wrong input data'})
        return jsonify(e.response), e.code


@delete_user_route.route('/api/iam/user/<id>', methods=['DELETE'])
@jwt_required()
def delete_user(id: str = 'self'):
    try:
        id = int(id)
    except ValueError:
        id = 'self'
    current_user = IamJwtUser()

    if not current_user.has_rights('iam_users_manage') and id != 'self':
        return jsonify({
            'error': f"User {current_user.identity['username']} doesn't have permissions to delete users"
        }), 403

    if id == 'self':
        user = current_user.get_db_obj()
    else:
        user = User.query.get(id)

    if user is None:
        return {'error': 'User not found.'}, 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'error': None})
