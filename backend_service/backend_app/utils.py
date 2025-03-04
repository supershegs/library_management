from typing import Optional, Any
from rest_framework.response import Response
from http import HTTPStatus


class ApiResponse(Response):
    def __init__(
        self,
        msg: str,
        status: int,
        data: Optional[Any] = None,
        errors: Optional[Any] = None,
    ):
        resp = {
            "status": status in range(200, 510),
            "message": msg,
            "data": data,
            "errors": errors,
        }
        super().__init__(data=resp, status=status)

    @classmethod
    def success(cls, msg: str, status: int,data: Optional[Any] = None):
        return cls(msg=msg, data=data, status=status)

    @classmethod
    def failure(cls, msg: str, status: int, errors: Optional[Any] = None):
        return cls(msg=msg, errors=errors, status=status)

    @classmethod
    def server_error(cls, msg: str, status: int):
        return cls(msg=msg, status=status)
