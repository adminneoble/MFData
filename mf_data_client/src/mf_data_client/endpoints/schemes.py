from typing import Any, Dict, List, Optional


class SchemesEndpoint:
    """Sync schemes endpoint."""

    def __init__(self, transport):
        self._t = transport

    def search(
        self,
        q: Optional[str] = None,
        amc_code: Optional[str] = None,
        status: Optional[str] = None,
        classcode: Optional[str] = None,
        amfi_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        params = {"page": page, "page_size": page_size}
        if q:
            params["q"] = q
        if amc_code:
            params["amc_code"] = amc_code
        if status:
            params["status"] = status
        if classcode:
            params["classcode"] = classcode
        if amfi_type:
            params["amfi_type"] = amfi_type
        return self._t.get("/api/v1/schemes", params=params)

    def get(self, schemecode: str) -> Dict[str, Any]:
        return self._t.get(f"/api/v1/schemes/{schemecode}")

    def get_master(self, schemecode: str) -> Dict[str, Any]:
        return self._t.get(f"/api/v1/schemes/{schemecode}/master")

    def bulk(self, schemecodes: List[str]) -> Dict[str, Any]:
        return self._t.post("/api/v1/schemes/bulk", json={"schemecodes": schemecodes})


class AsyncSchemesEndpoint:
    """Async schemes endpoint."""

    def __init__(self, transport):
        self._t = transport

    async def search(
        self,
        q: Optional[str] = None,
        amc_code: Optional[str] = None,
        status: Optional[str] = None,
        classcode: Optional[str] = None,
        amfi_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        params = {"page": page, "page_size": page_size}
        if q:
            params["q"] = q
        if amc_code:
            params["amc_code"] = amc_code
        if status:
            params["status"] = status
        if classcode:
            params["classcode"] = classcode
        if amfi_type:
            params["amfi_type"] = amfi_type
        return await self._t.get("/api/v1/schemes", params=params)

    async def get(self, schemecode: str) -> Dict[str, Any]:
        return await self._t.get(f"/api/v1/schemes/{schemecode}")

    async def get_master(self, schemecode: str) -> Dict[str, Any]:
        return await self._t.get(f"/api/v1/schemes/{schemecode}/master")

    async def bulk(self, schemecodes: List[str]) -> Dict[str, Any]:
        return await self._t.post("/api/v1/schemes/bulk", json={"schemecodes": schemecodes})
