from iam.models import User


class DataValidationError(BaseException):
    def __init__(self, msg: str, code: int = 400):
        self.code = code
        self.msg = msg

    @property
    def response(self) -> dict:
        return {'error': self.msg}


def validate_username(username: str):
    if username is None:
        raise DataValidationError('Username can\'t be null.')
    if len(username) <= 3:
        raise DataValidationError('Username must be longer than 3 symbols.')
    if len(username) > 122:
        raise DataValidationError('Username can\'t be longer than 122 symbols.')
    user = User.query.filter_by(username=username).first()
    if user is not None:
        raise DataValidationError(f'Username already exists.')


def validate_name(name: str):
    if name is None or name == '':
        return
    if len(name) > 122:
        raise DataValidationError('Name can\'t be longer than 122 symbols.')


def validate_password(password: str):
    if password is None:
        raise DataValidationError('Password can\'t be null')
    if len(password) <= 6:
        raise DataValidationError('Password must be longer than 6 symbols.')
    if len(password) > 24:
        raise DataValidationError('Password can\'t be longer than 24 symbols.')


def validate_group_name(name: str):
    if len(name) <= 3:
        raise DataValidationError('Group name must be longer than 3 symbols.')
    if len(name) > 122:
        raise DataValidationError('Group name can\'t be longer than 122 symbols.')
