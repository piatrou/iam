import os

from flask import Flask
from iam.models import db, migrate
from iam.routes.token import get_token_route, refresh_token_route
from iam.routes.user import \
    create_user_route,\
    get_users_route, \
    get_user_route, \
    edit_user_route, \
    delete_user_route
from iam.routes.group import \
    create_group_route, \
    get_groups_route, \
    get_group_route, \
    edit_group_route, \
    delete_group_route
from iam.routes.permissions import permission_controller
from flask_jwt_extended import JWTManager


def create_app():
    app: Flask = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///iam.db',
        JWT_SECRET_KEY='dev'
    )
    JWTManager(app)

    app.config.from_pyfile('iam_config.py', silent=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db, compare_type=True)
    app.app_context().push()
    db.create_all()

    for route in [
        get_token_route,
        refresh_token_route,
        create_user_route,
        get_users_route,
        get_user_route,
        edit_user_route,
        delete_user_route,
        create_group_route,
        get_groups_route,
        get_group_route,
        edit_group_route,
        delete_group_route,
        *permission_controller.get_routes()
    ]:
        app.register_blueprint(route)
    return app


app = create_app()

if __name__ == "__main__":
    app.run()
