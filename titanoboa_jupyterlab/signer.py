import json
from asyncio import sleep, get_running_loop
from datetime import timedelta
from multiprocessing.shared_memory import SharedMemory
from os import urandom
from typing import Any

import nest_asyncio
from IPython.display import display, Javascript

nest_asyncio.apply()
_TIMEOUT = timedelta(minutes=3)
_ADDRESS_LENGTH = 45  # 42 + quotes + \0
_TOKEN_LENGTH = 32
_TX_LENGTH = 2048
_NUL = b"\0"


class BrowserSigner:
    """
    A BrowserSigner is a class that can be used to sign transactions in IPython/JupyterLab.
    """
    def __init__(self, address=None):
        if address:
            self.address = address
        else:
            # wait for the address to be set via the API, otherwise boa crashes when trying to create a transaction
            self.address = _create_and_wait(_load_signer_snippet, size=_ADDRESS_LENGTH)

    def send_transaction(self, tx_data: dict) -> dict:
        """
        Implements the Account class' send_transaction method.
        It executes a Javascript snippet that requests the user's signature for the transaction.
        Then, it waits for the signature to be received via the API.
        :param tx_data: The transaction data to sign.
        :return: The signed transaction data.
        """
        sign_data = _create_and_wait(
            _sign_transaction_snippet,
            size=_TX_LENGTH,
            tx_data=tx_data,
        )
        return {k: int(v) if isinstance(v, str) and v.isnumeric() else v for k, v in sign_data.items() if v}


def _create_and_wait(snippet: callable, size: int, **kwargs) -> dict:
    """
    Create a SharedMemory object and wait for it to be filled with data.
    :param snippet: A function that given a token and some kwargs, returns a Javascript snippet.
    :param size: The size of the SharedMemory object to create.
    :param kwargs: The arguments to pass to the Javascript snippet.
    :return: The result of the Javascript snippet sent to the API.
    """
    token = f"titanoboa_jupyterlab_{urandom(_TOKEN_LENGTH).hex()}"
    memory = SharedMemory(name=token, create=True, size=size)
    try:
        memory.buf[:1] = _NUL
        javascript = snippet(token, **kwargs)
        display(javascript)
        return _wait_buffer_set(memory.buf)
    finally:
        memory.unlink()  # get rid of the SharedMemory object after it's been used


def _wait_buffer_set(buffer: memoryview):
    """
    Wait for the SharedMemory object to be filled with data.
    :param buffer: The buffer to wait for.
    :return: The contents of the buffer.
    """
    async def _wait_value(deadline: float) -> Any:
        """
        Wait until the SharedMemory object is not empty.
        :param deadline: The deadline to wait for.
        :return: The result of the Javascript snippet sent to the API.
        """
        inner_loop = get_running_loop()
        while buffer.tobytes().startswith(_NUL):
            if inner_loop.time() > deadline:
                raise TimeoutError("Timeout while waiting for user to confirm transaction in the browser.")
            await sleep(1)
        return json.loads(buffer.tobytes().decode().split("\0")[0])

    loop = get_running_loop()
    future = _wait_value(deadline=loop.time() + _TIMEOUT.total_seconds())
    task = loop.create_task(future)
    loop.run_until_complete(task)
    return task.result()


def _load_signer_snippet(token: str) -> Javascript:
    """ Runs the loadSigner in the browser. """
    return Javascript(f"window._titanoboa.loadSigner('{token}');")


def _sign_transaction_snippet(token: str, tx_data):
    """ Runs the signTransaction in the browser. """
    return Javascript(f"window._titanoboa.signTransaction('{token}', {json.dumps(tx_data)})")
