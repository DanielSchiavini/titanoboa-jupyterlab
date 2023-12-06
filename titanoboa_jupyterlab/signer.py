import json
from asyncio import Future, sleep, get_running_loop
from base64 import b64encode
from os import urandom
from typing import Optional, Callable, Any

from IPython.display import display, Javascript

from titanoboa_jupyterlab.memory import Memory
import nest_asyncio
nest_asyncio.apply()


class BrowserSigner:
    def __init__(self, address=None):
        self._future: Optional[Future] = None
        self._unique_id = b64encode(urandom(50)).decode()
        Memory.addresses[self._unique_id] = address

        if not address:
            self._display_and_wait(
                Javascript(f"window._titanoboa.loadSigner('{self._unique_id}');"),
                lambda: Memory.addresses[self._unique_id]
            )

    @property
    def address(self):
        return Memory.addresses[self._unique_id]

    def send_transaction(self, tx_data):
        if not self.address:
            raise ValueError("Cannot send transaction without address")
        sign_data = self._display_and_wait(
            Javascript(f"window._titanoboa.signTransaction('{self._unique_id}', {json.dumps(tx_data)})"),
            lambda: Memory.signatures.get(self._unique_id),
        )
        return {k: int(v) if isinstance(v, str) and v.isnumeric() else v for k, v in sign_data.items() if v}

    def _display_and_wait(self, javascript, get: Callable[[], Optional[Any]]):
        display(javascript)
        loop = get_running_loop()
        task = loop.create_task(self._wait_value(get))
        loop.run_until_complete(task)
        return get()

    @staticmethod
    async def _wait_value(get: Callable[[], Optional[Any]]):
        while not get():
            await sleep(0.001)

    def __del__(self):
        del Memory.addresses[self._unique_id]
        del Memory.signatures[self._unique_id]