from iam.common.jwt_user import JwtUser
from iam.models import User


class IamJwtUser(JwtUser):
    def get_db_obj(self) -> User:
        return User.query.filter_by(id=self.identity['id']).first()
