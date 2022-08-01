# pylint: disable=redefined-outer-name
from pathlib import Path
import shutil
import sys

import pytest

# Path hacks to make the code available for testing
LOCATION = Path(__file__).parent
sys.path.insert(0, str(LOCATION.parent))
sys.path.insert(0, str(LOCATION.parent / "src"))


@pytest.fixture
def root_path():
    return LOCATION


@pytest.fixture
def ruleset_path():
    return LOCATION / "mock_data/ruleset.dcp"


@pytest.fixture
def input_path(monkeypatch):
    mock_input_path = LOCATION / "mock_data/input"
    monkeypatch.setenv("UP42_INPUT_PATH", str(mock_input_path))
    return mock_input_path


@pytest.fixture
def output_path(monkeypatch):
    mock_output_path = LOCATION / "mock_data/output"
    monkeypatch.setenv("UP42_OUTPUT_PATH", str(mock_output_path))
    return mock_output_path


@pytest.fixture
def quicklook_path(monkeypatch):
    mock_quicklook_path = LOCATION / "mock_data/quicklook"
    monkeypatch.setenv("UP42_QUICKLOOK_PATH", str(mock_quicklook_path))
    return mock_quicklook_path


# pylint: disable=import-outside-toplevel
@pytest.fixture
def ecognition():
    from src import ecognition

    return ecognition


@pytest.fixture
def test_ready_env(input_path, output_path, quicklook_path):
    # Setup paths
    paths = [input_path, output_path, quicklook_path]
    for path in paths:
        path.mkdir(exist_ok=True)
    yield
    # Teardown paths
    for path in paths:
        shutil.rmtree(path)


# pylint: disable=unused-argument,unused-import,import-outside-toplevel
@pytest.fixture
def run_main(test_ready_env):
    def _main():
        from src import __main__

    yield _main
