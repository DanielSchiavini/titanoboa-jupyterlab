import json
from asyncio import sleep, get_running_loop
from base64 import b64encode
from datetime import timedelta
from os import urandom
from typing import Optional, Callable, Any

import nest_asyncio
from IPython.display import display, Javascript

from titanoboa_jupyterlab.memory import SharedMemory

TIMEOUT = timedelta(minutes=3)
nest_asyncio.apply()


class BrowserSigner:
    """
    A BrowserSigner is a class that can be used to sign transactions in IPython/JupyterLab.
    """
    def __init__(self, address=None):
        self._token = b64encode(urandom(50)).decode()
        self.memory = SharedMemory()

        # we already set the address in memory even if None, so the API can validate the token's validity
        self.memory.addresses[self._token] = address

        if not address:
            # wait for the address to be set via the API, otherwise boa will crash when trying to create a transaction
            self._run_and_wait(
                javascript=_load_signer_snippet(self._token),
                wait_until=lambda: self.memory.addresses[self._token]
            )

    @property
    def address(self):
        """
        Returns the sender address of the BrowserSigner. This is retrieved from the shared memory object.
        The value is expected to be received via the API.
        """
        return self.memory.addresses[self._token]

    def send_transaction(self, tx_data: dict):
        """
        Implements the Account class' send_transaction method.
        It executes a Javascript snippet that requests the user's signature for the transaction.
        Then, it waits for the signature to be received via the API.
        :param tx_data: The transaction data to sign.
        :return: The signed transaction data.
        """
        sign_data = self._run_and_wait(
            javascript=_sign_transaction_snippet(self._token, tx_data),
            wait_until=lambda: self.memory.signatures.get(self._token),
        )
        return {k: int(v) if isinstance(v, str) and v.isnumeric() else v for k, v in sign_data.items() if v}

    def _run_and_wait(self, javascript: Javascript, wait_until: Callable[[], Optional[Any]]):
        """
        Run a Javascript snippet via iPython and wait until a response is received.
        :param javascript: The Javascript snippet to run.
        :param wait_until: A function that returns a Truthy value when the wait is over.
        :return: The result of the Javascript snippet.
        """
        display(javascript)
        loop = get_running_loop()
        task = loop.create_task(self._wait_value(wait_until))
        loop.run_until_complete(task)
        return wait_until()

    @staticmethod
    async def _wait_value(wait_until: Callable[[], Optional[Any]]) -> Optional[Any]:
        """
        Simple helper function to wait until a value is not Falsy.
        :param wait_until: A function that returns a Truthy value when the wait is over.
        :return: The result of the wait_until function.
        """
        result = wait_until()
        loop = get_running_loop()
        deadline = loop.time() + TIMEOUT.total_seconds()
        while not result:
            if loop.time() > deadline:
                raise TimeoutError("Timeout while waiting for user to confirm.")
            await sleep(0.01)
            result = wait_until()
        return result

    def __del__(self):
        """
        The memory object needs to be closed when the BrowserSigner is deleted. Otherwise, we cause a memory leak.
        """
        self.memory.addresses.pop(self._token)
        self.memory.signatures.pop(self._token, None)
        self.memory.close()


def _load_signer_snippet(token: str) -> Javascript:
    """ Runs the loadSigner in the browser. """
    return Javascript(f"window._titanoboa.loadSigner('{token}');")


def _sign_transaction_snippet(token: str, tx_data):
    """ Runs the signTransaction in the browser. """
    return Javascript(f"window._titanoboa.signTransaction('{token}', {json.dumps(tx_data)})")
