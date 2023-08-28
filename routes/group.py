from iam.common.rest.controller import RestController
from iam.models import Group, db, Permission
from iam.common.jwt_user import JwtUser
from flask import request


class GroupRestController(RestController):
    def create_prepare_data(self, user: JwtUser, req: request) -> dict:
        return {
            'name': str(request.json.get('name', None))
        }

    def edit_prepare_data(self, entity, user: JwtUser, req: request):
        name = request.json.get('name', None)
        permissions = request.json.get('permissions', None)

        if name is not None:
            name = str(name)
            entity.name = name

        if permissions is not None:
            permissions = list(permissions)
            entity.permissions = Permission.query.filter(Permission.name.in_(permissions)).all()


group_controller = GroupRestController(
    'group',
    model=Group,
    api_path='/api/iam',
    db=db,
    create_permission='iam_group_manage',
    delete_permission='iam_group_manage',
    list_permission='iam_group_manage',
    get_permission='iam_group_manage',
    edit_permission='iam_group_manage'
)
