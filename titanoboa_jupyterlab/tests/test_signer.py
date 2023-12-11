import json
from unittest.mock import ANY
import re
from asyncio import sleep, Future
from multiprocessing.shared_memory import SharedMemory
from unittest.mock import MagicMock, patch

import pytest

from titanoboa_jupyterlab.signer import BrowserSigner


@pytest.fixture
def mock_display():
    mock = MagicMock()
    patcher = patch("titanoboa_jupyterlab.signer.display", mock)
    patcher.start()
    yield mock
    patcher.stop()


def test_address_given(mock_display):
    assert BrowserSigner("0x1234").address == "0x1234"
    assert mock_display.call_count == 0


@pytest.mark.gen_test
async def test_no_address_given(mock_display, io_loop):
    future = Future()
    io_loop.call_at(0, lambda: future.set_result(BrowserSigner()))
    await sleep(0.001)

    mock_display.assert_called_once_with(ANY)
    search = re.search(r"^window._titanoboa.loadSigner\('(.*)'\);$", mock_display.call_args[0][0].data)
    assert search

    memory = SharedMemory(search.group(1))
    body = b'"0x1234"\0'
    memory.buf[:len(body)] = body

    assert (await future).address == "0x1234"


@pytest.mark.gen_test
async def test_send_transaction(mock_display, io_loop):
    future = Future()
    browser = BrowserSigner("0x1234")
    io_loop.call_at(0, lambda: future.set_result(browser.send_transaction({"hash": "0x1234"})))
    await sleep(0.001)

    mock_display.assert_called_once_with(ANY)
    js, = mock_display.call_args[0]
    search = re.search(r"^window._titanoboa.signTransaction\('(.*)', (.*)\);$", js.data)
    assert search, f"Cannot match {js.data}"
    assert json.loads(search.group(2)) == {"hash": "0x1234"}

    memory = SharedMemory(search.group(1))
    body = b'{"signature": "0x4321"}\0'
    memory.buf[:len(body)] = body

    assert await future == {"signature": "0x4321"}
