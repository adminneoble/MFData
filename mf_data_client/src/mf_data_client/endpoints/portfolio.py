from typing import Any, Dict, Optional


class PortfolioEndpoint:
    def __init__(self, transport):
        self._t = transport

    def get(
        self,
        schemecode: str,
        as_of_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        params = {"page": page, "page_size": page_size}
        if as_of_date:
            params["as_of_date"] = as_of_date
        return self._t.get(f"/api/v1/portfolio/{schemecode}", params=params)

    def equity_holdings(
        self, schemecode: str, as_of_date: Optional[str] = None
    ) -> Dict[str, Any]:
        params = {}
        if as_of_date:
            params["as_of_date"] = as_of_date
        return self._t.get(f"/api/v1/portfolio/{schemecode}/equity-holdings", params=params)


class AsyncPortfolioEndpoint:
    def __init__(self, transport):
        self._t = transport

    async def get(
        self,
        schemecode: str,
        as_of_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        params = {"page": page, "page_size": page_size}
        if as_of_date:
            params["as_of_date"] = as_of_date
        return await self._t.get(f"/api/v1/portfolio/{schemecode}", params=params)

    async def equity_holdings(
        self, schemecode: str, as_of_date: Optional[str] = None
    ) -> Dict[str, Any]:
        params = {}
        if as_of_date:
            params["as_of_date"] = as_of_date
        return await self._t.get(f"/api/v1/portfolio/{schemecode}/equity-holdings", params=params)
