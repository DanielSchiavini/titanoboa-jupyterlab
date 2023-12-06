from http import HTTPStatus
from typing import Callable, TYPE_CHECKING

import tornado

if TYPE_CHECKING:
    from titanoboa_jupyterlab.handlers import BaseAPIHandler


def validate_callback_token(
        handler_method: Callable[["BaseAPIHandler", str, dict], None]
) -> Callable[["BaseAPIHandler"], None]:
    """
    Validates the token in the request body and parses the JSON data in the body.
    :param handler_method: The function to wrap
    :return: The wrapped function
    """

    def wrapper(self: "BaseAPIHandler"):
        data = tornado.escape.json_decode(self.request.body)
        token = data.pop("token", None)
        if token not in self.memory.addresses:
            self.set_status(HTTPStatus.BAD_REQUEST)
            self.finish({"message": f"Invalid token: {token}"})
            return
        return handler_method(self, token, data)

    return wrapper
