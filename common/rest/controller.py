from flask_sqlalchemy import SQLAlchemy
from iam.common.jwt_user import JwtUser
from iam.common.rest.errors import PermissionDenied, RestError, NotFound
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required
from typing import Union


def check_permissions(user, permission):
    if not user.has_rights(permission):
        raise PermissionDenied(f'User {user.identity["username"]} has no "{permission}" permissions')


def success(code: int = 200) -> tuple[Response, int]:
    return jsonify({'error': None}), code


class RestController:
    create_route: Blueprint = None
    delete_route: Blueprint = None
    list_route: Blueprint = None
    get_route: Blueprint = None
    edit_route: Blueprint = None
    list_per_page = 10

    def __init__(
            self,
            code: str,
            model,
            api_path: str,
            db: SQLAlchemy,
            create_auth_required: bool = True,
            delete_auth_required: bool = True,
            list_auth_required: bool = True,
            get_auth_required: bool = True,
            edit_auth_required: bool = True,
            create_permission: str = None,
            delete_permission: str = None,
            list_permission: str = None,
            get_permission: str = None,
            edit_permission: str = None
    ):
        self.code = code
        self.model = model
        self.api_path = api_path
        self.db = db
        self.create_auth_required = create_auth_required
        self.delete_auth_required = delete_auth_required
        self.list_auth_required = list_auth_required
        self.get_auth_required = get_auth_required
        self.edit_auth_required = edit_auth_required
        self.create_permission = create_permission
        self.delete_permission = delete_permission
        self.list_permission = list_permission
        self.get_permission = get_permission
        self.edit_permission = edit_permission

        self.init_blueprints()
        self.init_create_route()
        self.init_delete_route()
        self.init_list_route()
        self.init_get_route()
        self.init_edit_route()

    def init_blueprints(self):
        self.create_route = Blueprint(f'create_{self.code}', __name__)
        self.delete_route = Blueprint(f'delete_{self.code}', __name__)
        self.list_route = Blueprint(f'list_{self.code}', __name__)
        self.get_route = Blueprint(f'get_{self.code}', __name__)
        self.edit_route = Blueprint(f'edit_{self.code}', __name__)

    def init_create_route(self):
        @self.create_route.route(f'{self.api_path}/{self.code}', methods=['POST'])
        @jwt_required(optional=not self.create_auth_required)
        def create_entity():
            try:
                user = JwtUser()
                self.create_check_perm(user, request)
                prepared_data = self.create_prepare_data(user, request)
                entity = self.model(**prepared_data)
                self.db.session.add(entity)
                self.db.session.commit()
                return success(201)
            except RestError as e:
                return e.response

    def create_prepare_data(self, user: JwtUser, req: request) -> dict:
        raise NotImplementedError

    def create_check_perm(self, user: JwtUser, req: request):
        if self.create_permission is not None:
            check_permissions(user, self.create_permission)

    def init_delete_route(self):
        @self.delete_route.route(f'{self.api_path}/{self.code}/<id>', methods=['DELETE'])
        @jwt_required(optional=not self.delete_auth_required)
        def delete_entity(id: Union[int, str]):
            try:
                user = JwtUser()
                id = self.delete_prepare_id(id, user, request)
                self.delete_check_perm(id, user, request)
                entity = self.model.query.get(id)
                if entity is None:
                    raise NotFound(f'{self.code} not found')
                self.db.session.delete(entity)
                self.db.session.commit()
                return success()
            except RestError as e:
                return e.response

    def delete_check_perm(self, id: Union[int, str], user: JwtUser, req: request):
        if self.delete_permission is not None:
            check_permissions(user, self.delete_permission)

    def delete_prepare_id(self, id: Union[int, str], user: JwtUser, req: request) -> Union[int, str]:
        return id

    def init_list_route(self):
        @self.list_route.route(f'{self.api_path}/{self.code}', methods=['GET'])
        @jwt_required(optional=not self.list_auth_required)
        def list_entity():
            try:
                user = JwtUser()
                self.list_check_perm(user, request)
                try:
                    page = int(request.args.get('page', 1))
                except ValueError:
                    page = 1
                entities = self.list_filters(
                    self.model.query,
                    user,
                    request
                ).paginate(
                    page=page,
                    per_page=self.list_per_page
                )
                return jsonify({
                    'error': None,
                    'data': [e.short for e in entities.items],
                    'pages': entities.pages,
                    'page': entities.page
                })
            except RestError as e:
                return e.response

    def list_check_perm(self, user: JwtUser, req: request):
        if self.list_permission is not None:
            check_permissions(user, self.delete_permission)

    def list_filters(self, query, user: JwtUser, req: request):
        search = request.args.get('search', None)
        if search is not None and search != '':
            return query.filter(self.model.name.like(f'%{search}%'))
        return query

    def init_get_route(self):
        @self.get_route.route(f'{self.api_path}/{self.code}/<id>', methods=['GET'])
        @jwt_required(optional=not self.get_auth_required)
        def get_entity(id: Union[int, str]):
            try:
                user = JwtUser()
                id = self.get_prepare_id(id, user, request)
                self.get_check_perm(id, user, request)
                entity = self.model.query.get(id)
                if entity is None:
                    raise NotFound(f'{self.code} not found')
                return jsonify({'error': None, 'data': entity.full})
            except RestError as e:
                return e.response

    def get_check_perm(self, id: Union[int, str], user: JwtUser, req: request):
        if self.get_permission is not None:
            check_permissions(user, self.get_permission)

    def get_prepare_id(self, id: Union[int, str], user: JwtUser, req: request) -> Union[int, str]:
        return id

    def init_edit_route(self):
        @self.edit_route.route(f'{self.api_path}/{self.code}/<id>', methods=['PUT'])
        @jwt_required(optional=not self.edit_auth_required)
        def edit_entity(id: Union[int, str]):
            try:
                user = JwtUser()
                id = self.edit_prepare_id(id, user, request)
                self.edit_check_perm(id, user, request)
                entity = self.model.query.get(id)
                if entity is None:
                    raise NotFound(f'{self.code} not found')
                self.edit_prepare_data(entity, user, request)
                self.db.session.commit()
                return success()
            except RestError as e:
                return e.response

    def edit_check_perm(self, id: Union[int, str], user: JwtUser, req: request):
        if self.get_permission is not None:
            check_permissions(user, self.edit_permission)

    def edit_prepare_id(self, id: Union[int, str], user: JwtUser, req: request) -> Union[int, str]:
        return id

    def edit_prepare_data(self, entity, user: JwtUser, req: request):
        raise NotImplementedError

    def get_routes(self) -> list:
        return [
            self.create_route,
            self.delete_route,
            self.list_route,
            self.get_route,
            self.edit_route
        ]
