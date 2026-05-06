from typing import Any, Dict, List


class LookupEndpoint:
    def __init__(self, transport):
        self._t = transport

    def by_isin(self, isin: str) -> Dict[str, Any]:
        return self._t.get(f"/api/v1/lookup/by-isin/{isin}")

    def by_name(self, scheme_name: str, limit: int = 20) -> Dict[str, Any]:
        return self._t.get(
            f"/api/v1/lookup/by-name/{scheme_name}",
            params={"limit": limit},
        )

    def resolve(self, isins: List[str]) -> Dict[str, Any]:
        return self._t.post("/api/v1/lookup/resolve", json={"isins": isins})


class AsyncLookupEndpoint:
    def __init__(self, transport):
        self._t = transport

    async def by_isin(self, isin: str) -> Dict[str, Any]:
        return await self._t.get(f"/api/v1/lookup/by-isin/{isin}")

    async def by_name(self, scheme_name: str, limit: int = 20) -> Dict[str, Any]:
        return await self._t.get(
            f"/api/v1/lookup/by-name/{scheme_name}",
            params={"limit": limit},
        )

    async def resolve(self, isins: List[str]) -> Dict[str, Any]:
        return await self._t.post("/api/v1/lookup/resolve", json={"isins": isins})
