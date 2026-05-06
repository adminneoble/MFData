from typing import Any, Dict, Optional


class FundManagersEndpoint:
    def __init__(self, transport):
        self._t = transport

    def search(
        self, q: Optional[str] = None, page: int = 1, page_size: int = 50
    ) -> Dict[str, Any]:
        params = {"page": page, "page_size": page_size}
        if q:
            params["q"] = q
        return self._t.get("/api/v1/fund-managers", params=params)

    def get(self, manager_id: str) -> Dict[str, Any]:
        return self._t.get(f"/api/v1/fund-managers/{manager_id}")

    def schemes(self, manager_id: str) -> Dict[str, Any]:
        return self._t.get(f"/api/v1/fund-managers/{manager_id}/schemes")


class AsyncFundManagersEndpoint:
    def __init__(self, transport):
        self._t = transport

    async def search(
        self, q: Optional[str] = None, page: int = 1, page_size: int = 50
    ) -> Dict[str, Any]:
        params = {"page": page, "page_size": page_size}
        if q:
            params["q"] = q
        return await self._t.get("/api/v1/fund-managers", params=params)

    async def get(self, manager_id: str) -> Dict[str, Any]:
        return await self._t.get(f"/api/v1/fund-managers/{manager_id}")

    async def schemes(self, manager_id: str) -> Dict[str, Any]:
        return await self._t.get(f"/api/v1/fund-managers/{manager_id}/schemes")
