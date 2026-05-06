"""Synchronous MFDataClient — the primary SDK entry point."""

from typing import Optional

from mf_data_client.transport import SyncTransport, _resolve_config
from mf_data_client.endpoints.schemes import SchemesEndpoint
from mf_data_client.endpoints.nav_history import NavHistoryEndpoint
from mf_data_client.endpoints.portfolio import PortfolioEndpoint
from mf_data_client.endpoints.performance import PerformanceEndpoint
from mf_data_client.endpoints.fund_managers import FundManagersEndpoint
from mf_data_client.endpoints.amcs import AMCsEndpoint
from mf_data_client.endpoints.lookup import LookupEndpoint
from mf_data_client.endpoints.snapshots import SnapshotsEndpoint
from mf_data_client.endpoints.admin import AdminEndpoint


class MFDataClient:
    """Synchronous client for MFDataService.

    Usage:
        with MFDataClient.from_env() as mf:
            scheme = mf.lookup.by_isin("INF846K01EW2")
            navs = mf.nav_history.get("1234")
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        url, key, tout = _resolve_config(base_url, api_key, timeout)
        self._transport = SyncTransport(url, key, tout)

        self.schemes = SchemesEndpoint(self._transport)
        self.nav_history = NavHistoryEndpoint(self._transport)
        self.portfolio = PortfolioEndpoint(self._transport)
        self.performance = PerformanceEndpoint(self._transport)
        self.fund_managers = FundManagersEndpoint(self._transport)
        self.amcs = AMCsEndpoint(self._transport)
        self.lookup = LookupEndpoint(self._transport)
        self.snapshots = SnapshotsEndpoint(self._transport)
        self.admin = AdminEndpoint(self._transport)

    @classmethod
    def from_env(cls) -> "MFDataClient":
        """Create client from MF_DATA_SERVICE_URL and MF_DATA_SERVICE_API_KEY env vars."""
        return cls()

    def health(self) -> dict:
        return self._transport.get("/api/v1/health")

    def close(self):
        self._transport.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
