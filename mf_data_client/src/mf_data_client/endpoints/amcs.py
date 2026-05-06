from typing import Any, Dict, Optional


class AMCsEndpoint:
    def __init__(self, transport):
        self._t = transport

    def list(
        self, q: Optional[str] = None, page: int = 1, page_size: int = 50
    ) -> Dict[str, Any]:
        params = {"page": page, "page_size": page_size}
        if q:
            params["q"] = q
        return self._t.get("/api/v1/amcs", params=params)

    def get(self, amc_code: str) -> Dict[str, Any]:
        return self._t.get(f"/api/v1/amcs/{amc_code}")

    def schemes(
        self,
        amc_code: str,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        params = {"page": page, "page_size": page_size}
        if status:
            params["status"] = status
        return self._t.get(f"/api/v1/amcs/{amc_code}/schemes", params=params)


class AsyncAMCsEndpoint:
    def __init__(self, transport):
        self._t = transport

    async def list(
        self, q: Optional[str] = None, page: int = 1, page_size: int = 50
    ) -> Dict[str, Any]:
        params = {"page": page, "page_size": page_size}
        if q:
            params["q"] = q
        return await self._t.get("/api/v1/amcs", params=params)

    async def get(self, amc_code: str) -> Dict[str, Any]:
        return await self._t.get(f"/api/v1/amcs/{amc_code}")

    async def schemes(
        self,
        amc_code: str,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        params = {"page": page, "page_size": page_size}
        if status:
            params["status"] = status
        return await self._t.get(f"/api/v1/amcs/{amc_code}/schemes", params=params)
