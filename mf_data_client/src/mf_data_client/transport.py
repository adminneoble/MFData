"""HTTP transport layer shared by sync and async clients."""

import os
from typing import Any, Dict, Optional

import httpx

from mf_data_client.exceptions import (
    AuthenticationError,
    MFDataClientError,
    NotFoundError,
    ServerError,
    ValidationError,
)

DEFAULT_BASE_URL = "http://localhost:8100"
DEFAULT_TIMEOUT = 30.0


def _resolve_config(
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: Optional[float] = None,
) -> tuple[str, Optional[str], float]:
    """Resolve config from args or environment variables."""
    base_url = base_url or os.environ.get("MF_DATA_SERVICE_URL", DEFAULT_BASE_URL)
    api_key = api_key or os.environ.get("MF_DATA_SERVICE_API_KEY")
    timeout = timeout or float(os.environ.get("MF_DATA_SERVICE_TIMEOUT", DEFAULT_TIMEOUT))
    return base_url.rstrip("/"), api_key, timeout


def _build_headers(api_key: Optional[str]) -> Dict[str, str]:
    headers = {"Accept": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key
    return headers


def _handle_response(response: httpx.Response) -> Any:
    """Check response status and return parsed JSON."""
    if response.status_code == 401:
        raise AuthenticationError("Invalid or missing API key")
    if response.status_code == 404:
        detail = response.json().get("detail", "Not found")
        raise NotFoundError(detail)
    if response.status_code == 422:
        raise ValidationError(str(response.json()))
    if response.status_code == 400:
        detail = response.json().get("detail", "Bad request")
        raise ValidationError(detail)
    if response.status_code >= 500:
        raise ServerError(f"Server error: {response.status_code}")
    response.raise_for_status()
    return response.json()


class SyncTransport:
    """Synchronous HTTP transport using httpx."""

    def __init__(self, base_url: str, api_key: Optional[str], timeout: float):
        self._base_url = base_url
        self._client = httpx.Client(
            base_url=base_url,
            headers=_build_headers(api_key),
            timeout=timeout,
        )

    def get(self, path: str, params: Optional[Dict] = None) -> Any:
        resp = self._client.get(path, params=params)
        return _handle_response(resp)

    def post(self, path: str, json: Optional[Dict] = None) -> Any:
        resp = self._client.post(path, json=json)
        return _handle_response(resp)

    def close(self):
        self._client.close()


class AsyncTransport:
    """Asynchronous HTTP transport using httpx."""

    def __init__(self, base_url: str, api_key: Optional[str], timeout: float):
        self._base_url = base_url
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=_build_headers(api_key),
            timeout=timeout,
        )

    async def get(self, path: str, params: Optional[Dict] = None) -> Any:
        resp = await self._client.get(path, params=params)
        return _handle_response(resp)

    async def post(self, path: str, json: Optional[Dict] = None) -> Any:
        resp = await self._client.post(path, json=json)
        return _handle_response(resp)

    async def close(self):
        await self._client.aclose()
