from flask_jwt_extended import get_jwt_identity


class JwtUser:
    def __init__(self):
        self.identity = get_jwt_identity()

    def has_rights(self, permission: str) -> bool:
        return permission in self.identity['permissions']
