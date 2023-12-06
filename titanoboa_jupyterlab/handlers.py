from http import HTTPStatus
from typing import Callable

import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join

from titanoboa_jupyterlab.memory import Memory


def validate_callback_key(f: Callable[[APIHandler, str, dict], None]) -> Callable[[APIHandler], None]:
    """
    Validates the key in the request body and parses the JSON data in the body.
    :param f: The function to wrap
    :return: The wrapped function
    """
    def wrapper(self):
        data = tornado.escape.json_decode(self.request.body)
        key = data.pop("key", None)
        if key not in Memory.addresses:
            self.set_status(HTTPStatus.BAD_REQUEST)
            self.finish({
                "message": f"Invalid key: {key}"
            })
            validate_callback_key.log.info(f"Invalid key: {key} from {list(Memory.addresses.keys())}")
            return
        return f(self, key, data)

    return wrapper


class SetSignerHandler(APIHandler):
    @tornado.web.authenticated  # ensure only authorized user can request the Jupyter server
    @validate_callback_key
    def post(self, key, data):
        Memory.addresses[key] = data["address"]
        self.set_status(HTTPStatus.NO_CONTENT)
        self.finish()


class SignTransactionHandler(APIHandler):
    @tornado.web.authenticated  # ensure only authorized user can request the Jupyter server
    @validate_callback_key
    def post(self, key, data):
        Memory.signatures[key] = data
        self.set_status(HTTPStatus.NO_CONTENT)
        self.finish()


def setup_handlers(server_app):
    web_app = server_app.web_app
    base_url = url_path_join(web_app.settings["base_url"], "titanoboa-jupyterlab")
    web_app.add_handlers(
        host_pattern=".*$",
        host_handlers=[
            (f"{base_url}/set_signer", SetSignerHandler, { "memory": memory }),
            (f"{base_url}/sign_transaction", SignTransactionHandler, { "memory": memory }),
        ]
    )
    validate_callback_key.log = server_app.log
    server_app.log.info(f"Handlers registered in {base_url}")
