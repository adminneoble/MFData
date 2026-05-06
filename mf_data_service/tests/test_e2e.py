"""
End-to-end integration tests.

Requires:
  1. MongoDB running on localhost:27017
  2. Data loaded via: python -m scripts.load_datadump --drop
  3. Service running via: ./run.sh

Run: pytest tests/test_e2e.py -v
"""

import os
import sys
import pytest

# Add SDK to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "mf_data_client", "src"))

try:
    from mf_data_client import MFDataClient
    from mf_data_client.exceptions import NotFoundError
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False


def _service_running() -> bool:
    if not SDK_AVAILABLE:
        return False
    try:
        with MFDataClient() as client:
            client.health()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _service_running(),
    reason="MFDataService not running on localhost:8100",
)


@pytest.fixture(scope="module")
def client():
    c = MFDataClient()
    yield c
    c.close()


class TestHealth:
    def test_health(self, client):
        result = client.health()
        assert result["status"] == "ok"


class TestSchemes:
    def test_search(self, client):
        result = client.schemes.search(page_size=5)
        assert "items" in result
        assert result["total"] > 0
        assert len(result["items"]) <= 5

    def test_search_by_name(self, client):
        result = client.schemes.search(q="HDFC", page_size=10)
        assert result["total"] > 0
        for item in result["items"]:
            assert "HDFC" in item["scheme_name"].upper() or "HDFC" in item.get("amfi_name", "").upper()

    def test_get_scheme(self, client):
        # Get first scheme from search
        search = client.schemes.search(page_size=1)
        schemecode = search["items"][0]["schemecode"]
        result = client.schemes.get(schemecode)
        assert result["data"]["schemecode"] == schemecode

    def test_get_nonexistent(self, client):
        with pytest.raises(NotFoundError):
            client.schemes.get("99999999")

    def test_bulk(self, client):
        search = client.schemes.search(page_size=3)
        codes = [item["schemecode"] for item in search["items"]]
        result = client.schemes.bulk(codes)
        assert result["count"] == len(codes)


class TestLookup:
    def test_by_name(self, client):
        result = client.lookup.by_name("Axis", limit=5)
        assert result["count"] > 0

    def test_resolve_bulk(self, client):
        result = client.lookup.resolve(["INF846K01EW2", "INVALID123456"])
        assert result["total"] == 2


class TestNavHistory:
    def test_latest_nav(self, client):
        search = client.schemes.search(page_size=1)
        code = search["items"][0]["schemecode"]
        result = client.nav_history.get_latest(code)
        assert "data" in result
        assert result["data"]["schemecode"] == code


class TestAMCs:
    def test_list(self, client):
        result = client.amcs.list(page_size=5)
        assert result["total"] > 0
        assert len(result["items"]) <= 5

    def test_get(self, client):
        amcs = client.amcs.list(page_size=1)
        amc_code = amcs["items"][0]["amc_code"]
        result = client.amcs.get(amc_code)
        assert result["data"]["amc_code"] == amc_code


class TestFundManagers:
    def test_search(self, client):
        result = client.fund_managers.search(page_size=5)
        assert result["total"] > 0


class TestAdmin:
    def test_datasets(self, client):
        result = client.admin.datasets()
        assert result["count"] > 50

    def test_stats(self, client):
        result = client.admin.stats()
        assert "data" in result


class TestSnapshots:
    def test_snapshot(self, client):
        search = client.schemes.search(page_size=1)
        code = search["items"][0]["schemecode"]
        result = client.snapshots.get(code)
        assert result["data"]["schemecode"] == code
