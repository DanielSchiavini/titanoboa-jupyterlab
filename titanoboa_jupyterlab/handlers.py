from http import HTTPStatus

import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join

from titanoboa_jupyterlab.helpers import validate_callback_token
from titanoboa_jupyterlab.memory import SharedMemory


class BaseAPIHandler(APIHandler):
    memory: SharedMemory

    def initialize(self):
        """ Initialize the shared memory object when the request is received. """
        self.memory = SharedMemory()

    def finish(self, *args, **kwargs):
        """ Close the shared memory object after the request is finished. """
        super().finish(*args, **kwargs)
        self.memory.close()


class SetSignerHandler(BaseAPIHandler):
    @tornado.web.authenticated  # ensure only authorized user can request the Jupyter server
    @validate_callback_token # ensure the token is valid and inject the data into the handler method
    def post(self, token: str, data: dict) -> None:
        self.memory.addresses[token] = data["address"]
        self.set_status(HTTPStatus.NO_CONTENT)
        self.finish()


class SignTransactionHandler(BaseAPIHandler):
    @tornado.web.authenticated  # ensure only authorized user can request the Jupyter server
    @validate_callback_token # ensure the token is valid and inject the data into the handler method
    def post(self, token: str, data: dict) -> None:
        self.memory.signatures[token] = data
        self.set_status(HTTPStatus.NO_CONTENT)
        self.finish()


def setup_handlers(server_app) -> None:
    """
    Register the handlers in the Jupyter server.
    :param server_app: The Jupyter server application.
    """
    web_app = server_app.web_app
    base_url = url_path_join(web_app.settings["base_url"], "titanoboa-jupyterlab")
    web_app.add_handlers(
        host_pattern=".*$",
        host_handlers=[
            (f"{base_url}/set_signer", SetSignerHandler),
            (f"{base_url}/send_transaction", SignTransactionHandler),
        ]
    )
    validate_callback_token.log = server_app.log
    server_app.log.info(f"Handlers registered in {base_url}")
