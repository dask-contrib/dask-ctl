import pytest
import os


@pytest.fixture
def simple_spec_path():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "specs", "simple.yaml"
    )
