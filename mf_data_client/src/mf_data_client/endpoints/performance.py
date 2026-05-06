from typing import Any, Dict, List


class PerformanceEndpoint:
    def __init__(self, transport):
        self._t = transport

    def get(self, schemecode: str) -> Dict[str, Any]:
        return self._t.get(f"/api/v1/performance/{schemecode}")

    def compare(self, schemecodes: List[str]) -> Dict[str, Any]:
        return self._t.get(
            "/api/v1/performance/compare",
            params={"schemecodes": ",".join(schemecodes)},
        )


class AsyncPerformanceEndpoint:
    def __init__(self, transport):
        self._t = transport

    async def get(self, schemecode: str) -> Dict[str, Any]:
        return await self._t.get(f"/api/v1/performance/{schemecode}")

    async def compare(self, schemecodes: List[str]) -> Dict[str, Any]:
        return await self._t.get(
            "/api/v1/performance/compare",
            params={"schemecodes": ",".join(schemecodes)},
        )
