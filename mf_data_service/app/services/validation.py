"""Data validation utilities."""

import re
from typing import Optional


def validate_isin(isin: str) -> bool:
    """Validate Indian ISIN format: IN + 10 alphanumeric chars = 12 total."""
    return bool(re.match(r"^IN[A-Z0-9]{10}$", isin))


def validate_schemecode(schemecode: str) -> bool:
    """Schemecode should be a numeric string."""
    return schemecode.isdigit()


def safe_float(value: Optional[str], default: float = 0.0) -> float:
    """Safely convert a string to float."""
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Optional[str], default: int = 0) -> int:
    """Safely convert a string to int."""
    if value is None or value == "":
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default
