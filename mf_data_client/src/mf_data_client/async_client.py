"""Asynchronous MFDataClient for high-concurrency scenarios."""

from typing import Optional

from mf_data_client.transport import AsyncTransport, _resolve_config
from mf_data_client.endpoints.schemes import AsyncSchemesEndpoint
from mf_data_client.endpoints.nav_history import AsyncNavHistoryEndpoint
from mf_data_client.endpoints.portfolio import AsyncPortfolioEndpoint
from mf_data_client.endpoints.performance import AsyncPerformanceEndpoint
from mf_data_client.endpoints.fund_managers import AsyncFundManagersEndpoint
from mf_data_client.endpoints.amcs import AsyncAMCsEndpoint
from mf_data_client.endpoints.lookup import AsyncLookupEndpoint
from mf_data_client.endpoints.snapshots import AsyncSnapshotsEndpoint
from mf_data_client.endpoints.admin import AsyncAdminEndpoint


class AsyncMFDataClient:
    """Async client for MFDataService.

    Usage:
        async with AsyncMFDataClient.from_env() as mf:
            scheme = await mf.lookup.by_isin("INF846K01EW2")
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        url, key, tout = _resolve_config(base_url, api_key, timeout)
        self._transport = AsyncTransport(url, key, tout)

        self.schemes = AsyncSchemesEndpoint(self._transport)
        self.nav_history = AsyncNavHistoryEndpoint(self._transport)
        self.portfolio = AsyncPortfolioEndpoint(self._transport)
        self.performance = AsyncPerformanceEndpoint(self._transport)
        self.fund_managers = AsyncFundManagersEndpoint(self._transport)
        self.amcs = AsyncAMCsEndpoint(self._transport)
        self.lookup = AsyncLookupEndpoint(self._transport)
        self.snapshots = AsyncSnapshotsEndpoint(self._transport)
        self.admin = AsyncAdminEndpoint(self._transport)

    @classmethod
    def from_env(cls) -> "AsyncMFDataClient":
        return cls()

    async def health(self) -> dict:
        return await self._transport.get("/api/v1/health")

    async def close(self):
        await self._transport.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
