import asyncio

import pytest
import os


@pytest.fixture
def simple_spec_path():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "specs", "simple.yaml"
    )


@pytest.fixture
def event_loop():
    yield asyncio.get_event_loop()


def pytest_sessionfinish(session, exitstatus):
    asyncio.get_event_loop().close()
