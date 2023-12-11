import json
from multiprocessing.shared_memory import SharedMemory

import pytest

from titanoboa_jupyterlab.signer import _generate_token


@pytest.fixture
def token():
    return _generate_token()


@pytest.fixture
def memory(token):
    memory = SharedMemory(name=token, create=True, size=1024)
    memory.buf[:1] = b"\0"
    yield lambda: memory.buf.tobytes().split(b"\0")[0]
    memory.unlink()


@pytest.fixture
def fetch_callback(jp_fetch, token):
    async def fetch(body=b"{}"):
        response = await jp_fetch(
            "titanoboa-jupyterlab",
            f"callback/{token}",
            method="POST", body=body, raise_error=False
        )
        return response.code, response.body and json.loads(response.body)
    return fetch


async def test_post_callback(fetch_callback, memory):
    response = await fetch_callback(body=b"1")
    assert response == (204, b"")
    assert memory() == b"1"


async def test_post_callback_unknown_token(fetch_callback, token):  # no memory injected
    assert await fetch_callback() == (404, {"message": f"Invalid token: {token}"})


async def test_post_callback_too_large(fetch_callback, memory):
    assert await fetch_callback(body=b"1" * 1024) == (
        413, {"message": "Request body has 1025 bytes, but only 1024 are allowed"}
    )
    assert memory() == b""


async def test_post_callback_no_body(fetch_callback, memory):
    assert await fetch_callback(b"") == (400, {"message": "Request body is required"})
    assert memory() == b""
