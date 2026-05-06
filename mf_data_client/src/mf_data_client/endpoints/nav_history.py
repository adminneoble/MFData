from typing import Any, Dict, List, Optional


class NavHistoryEndpoint:
    def __init__(self, transport):
        self._t = transport

    def get(
        self,
        schemecode: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        params = {"page": page, "page_size": page_size}
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date
        return self._t.get(f"/api/v1/nav-history/{schemecode}", params=params)

    def get_latest(self, schemecode: str) -> Dict[str, Any]:
        return self._t.get(f"/api/v1/nav-history/{schemecode}/latest")

    def bulk(self, schemecodes: List[str]) -> Dict[str, Any]:
        return self._t.post("/api/v1/nav-history/bulk", json={"schemecodes": schemecodes})


class AsyncNavHistoryEndpoint:
    def __init__(self, transport):
        self._t = transport

    async def get(
        self,
        schemecode: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        params = {"page": page, "page_size": page_size}
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date
        return await self._t.get(f"/api/v1/nav-history/{schemecode}", params=params)

    async def get_latest(self, schemecode: str) -> Dict[str, Any]:
        return await self._t.get(f"/api/v1/nav-history/{schemecode}/latest")

    async def bulk(self, schemecodes: List[str]) -> Dict[str, Any]:
        return await self._t.post("/api/v1/nav-history/bulk", json={"schemecodes": schemecodes})
