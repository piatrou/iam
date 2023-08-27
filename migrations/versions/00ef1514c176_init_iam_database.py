"""init iam database

Revision ID: 00ef1514c176
Revises: 
Create Date: 2023-07-14 22:07:31.273326

"""
from alembic import op
import sqlalchemy as sa
from iam.models import Permission, Group, User
from werkzeug.security import generate_password_hash


# revision identifiers, used by Alembic.
revision = '00ef1514c176'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.bulk_insert(User.__table__, [
        {
            'active': True,
            'username': 'admin',
            'password_hash': generate_password_hash('admin')

        }
    ])
    op.bulk_insert(Group.__table__, [
        {
            'name': 'users',
        },
        {
            'name': 'admins',
        }
    ])
    op.bulk_insert(Permission.__table__, [
        {
            'name': 'iam_users_manage',
            'description': 'Permissions to manage users'
        },
        {
            'name': 'iam_group_manage',
            'description': 'Permissions to manage groups'
        },
        {
            'name': 'iam_permission_manage',
            'description': 'Permissions to manage groups'
        }

    ])

    op.execute(
        "insert into users_to_groups (group_id, user_id) "
        "select g.id, u.id from `group` g, `user` u "
        "where g.name = 'admins' and u.username = 'admin'"
    )
    op.execute(
        "insert into group_to_permissions (permission_id, group_id) "
        "select p.id, g.id from `permission` p, `group` g "
        "where g.name = 'admins'"
    )
    # op.execute(
    #     "insert into group_to_permissions (permission_id, group_id) "
    #     "select p.id, g.id from `permission` p, `group` g "
    #     "where g.name = 'users' and p.name = 'iam_change_password'"
    # )


def downgrade():
    op.execute(
        "delete from group_to_permissions "
        "where group_id = (select id from `group` where name = 'users')"
    )
    op.execute(
        "delete from group_to_permissions "
        "where group_id = (select id from `group` where name = 'admins')"
    )
    op.execute(
        'delete from "group" '
        "where name in ('admins', 'users')"
    )
    op.execute(
        'delete from "permission" '
        "where name in ('iam_users_manage', 'iam_group_manage', 'iam_permission_manage')"
    )
    op.execute(
        'delete from "user" '
        "where username = 'admin'"
    )
