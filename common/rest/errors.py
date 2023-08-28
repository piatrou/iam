from flask import jsonify, Response


class RestError(BaseException):
    code = 400

    def __init__(self, msg: str, code: int = None):
        if code is not None:
            self.code = code
        self.msg = msg

    @property
    def response(self) -> tuple[Response, int]:
        return jsonify({'error': self.msg}), self.code


class PermissionDenied(RestError):
    code = 403


class NotFound(RestError):
    code = 404
