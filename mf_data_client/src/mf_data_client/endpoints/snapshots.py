from typing import Any, Dict, List


class SnapshotsEndpoint:
    def __init__(self, transport):
        self._t = transport

    def get(self, schemecode: str) -> Dict[str, Any]:
        return self._t.get(f"/api/v1/scheme-snapshot/{schemecode}")

    def bulk(self, schemecodes: List[str]) -> Dict[str, Any]:
        return self._t.post(
            "/api/v1/scheme-snapshot/bulk",
            json={"schemecodes": schemecodes},
        )


class AsyncSnapshotsEndpoint:
    def __init__(self, transport):
        self._t = transport

    async def get(self, schemecode: str) -> Dict[str, Any]:
        return await self._t.get(f"/api/v1/scheme-snapshot/{schemecode}")

    async def bulk(self, schemecodes: List[str]) -> Dict[str, Any]:
        return await self._t.post(
            "/api/v1/scheme-snapshot/bulk",
            json={"schemecodes": schemecodes},
        )
