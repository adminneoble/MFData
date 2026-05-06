class MFDataClientError(Exception):
    """Base exception for MFDataClient."""


class NotFoundError(MFDataClientError):
    """Resource not found (404)."""


class AuthenticationError(MFDataClientError):
    """Invalid or missing API key (401)."""


class ValidationError(MFDataClientError):
    """Invalid request parameters (400/422)."""


class ServerError(MFDataClientError):
    """Server-side error (5xx)."""
