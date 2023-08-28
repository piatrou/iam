from iam.common.rest.controller import RestController
from iam.models import Permission, db
from iam.common.jwt_user import JwtUser
from flask import request


class PermissionRestController(RestController):
    def create_prepare_data(self, user: JwtUser, req: request) -> dict:
        return {
            'name': str(request.json.get('name', None)),
            'description': str(request.json.get('description', None))
        }

    def edit_prepare_data(self, entity, user: JwtUser, req: request):
        name = request.json.get('name', None)
        description = request.json.get('description', None)

        if name is not None:
            name = str(name)
            entity.name = name

        if description is not None:
            description = str(description)
            entity.description = description


permission_controller = PermissionRestController(
    'permission',
    model=Permission,
    api_path='/api/iam',
    db=db,
    create_permission='iam_permission_manage',
    delete_permission='iam_permission_manage',
    list_permission='iam_permission_manage',
    get_permission='iam_permission_manage',
    edit_permission='iam_permission_manage'
)
