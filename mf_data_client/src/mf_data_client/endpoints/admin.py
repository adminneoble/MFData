from typing import Any, Dict, List, Optional


class AdminEndpoint:
    def __init__(self, transport):
        self._t = transport

    def load_datadump(
        self,
        datasets: Optional[List[str]] = None,
        drop_existing: bool = False,
    ) -> Dict[str, Any]:
        return self._t.post(
            "/api/v1/admin/load-datadump",
            json={"datasets": datasets, "drop_existing": drop_existing},
        )

    def load_dataset(self, dataset_name: str, drop_existing: bool = False) -> Dict[str, Any]:
        return self._t.post(
            f"/api/v1/admin/load-datadump/{dataset_name}",
            json={"drop_existing": drop_existing},
        )

    def datasets(self) -> Dict[str, Any]:
        return self._t.get("/api/v1/admin/datasets")

    def stats(self) -> Dict[str, Any]:
        return self._t.get("/api/v1/admin/stats")

    def validate(self) -> Dict[str, Any]:
        return self._t.post("/api/v1/admin/validate")


class AsyncAdminEndpoint:
    def __init__(self, transport):
        self._t = transport

    async def load_datadump(
        self,
        datasets: Optional[List[str]] = None,
        drop_existing: bool = False,
    ) -> Dict[str, Any]:
        return await self._t.post(
            "/api/v1/admin/load-datadump",
            json={"datasets": datasets, "drop_existing": drop_existing},
        )

    async def load_dataset(self, dataset_name: str, drop_existing: bool = False) -> Dict[str, Any]:
        return await self._t.post(
            f"/api/v1/admin/load-datadump/{dataset_name}",
            json={"drop_existing": drop_existing},
        )

    async def datasets(self) -> Dict[str, Any]:
        return await self._t.get("/api/v1/admin/datasets")

    async def stats(self) -> Dict[str, Any]:
        return await self._t.get("/api/v1/admin/stats")

    async def validate(self) -> Dict[str, Any]:
        return await self._t.post("/api/v1/admin/validate")
