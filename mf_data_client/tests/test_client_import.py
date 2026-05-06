"""Smoke tests for mf_data_client SDK (no server needed)."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_import():
    from mf_data_client import MFDataClient, AsyncMFDataClient
    assert MFDataClient is not None
    assert AsyncMFDataClient is not None


def test_client_construction():
    from mf_data_client import MFDataClient
    client = MFDataClient(base_url="http://localhost:9999")
    assert hasattr(client, "schemes")
    assert hasattr(client, "nav_history")
    assert hasattr(client, "portfolio")
    assert hasattr(client, "performance")
    assert hasattr(client, "fund_managers")
    assert hasattr(client, "amcs")
    assert hasattr(client, "lookup")
    assert hasattr(client, "snapshots")
    assert hasattr(client, "admin")
    client.close()


def test_context_manager():
    from mf_data_client import MFDataClient
    with MFDataClient(base_url="http://localhost:9999") as client:
        assert client.schemes is not None


def test_from_env():
    from mf_data_client import MFDataClient
    os.environ["MF_DATA_SERVICE_URL"] = "http://test:1234"
    os.environ["MF_DATA_SERVICE_API_KEY"] = "test-key"
    client = MFDataClient.from_env()
    assert client._transport._base_url == "http://test:1234"
    client.close()
    del os.environ["MF_DATA_SERVICE_URL"]
    del os.environ["MF_DATA_SERVICE_API_KEY"]


def test_exceptions():
    from mf_data_client.exceptions import (
        MFDataClientError,
        NotFoundError,
        AuthenticationError,
        ValidationError,
        ServerError,
    )
    assert issubclass(NotFoundError, MFDataClientError)
    assert issubclass(AuthenticationError, MFDataClientError)
    assert issubclass(ServerError, MFDataClientError)
