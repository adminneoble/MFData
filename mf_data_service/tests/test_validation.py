"""Unit tests for validation utilities."""

from app.services.validation import validate_isin, validate_schemecode, safe_float, safe_int


class TestValidateISIN:
    def test_valid_isin(self):
        assert validate_isin("INF846K01EW2") is True
        assert validate_isin("INF00XX01135") is True

    def test_invalid_isin(self):
        assert validate_isin("") is False
        assert validate_isin("US1234567890") is False
        assert validate_isin("INF846") is False
        assert validate_isin("inf846k01ew2") is False  # lowercase


class TestValidateSchemecode:
    def test_valid(self):
        assert validate_schemecode("1234") is True
        assert validate_schemecode("49252") is True

    def test_invalid(self):
        assert validate_schemecode("") is False
        assert validate_schemecode("abc") is False


class TestSafeFloat:
    def test_normal(self):
        assert safe_float("456.78") == 456.78
        assert safe_float("0") == 0.0

    def test_empty(self):
        assert safe_float("") == 0.0
        assert safe_float(None) == 0.0

    def test_invalid(self):
        assert safe_float("abc") == 0.0

    def test_custom_default(self):
        assert safe_float("", default=-1.0) == -1.0


class TestSafeInt:
    def test_normal(self):
        assert safe_int("42") == 42
        assert safe_int("3.7") == 3  # truncates

    def test_empty(self):
        assert safe_int("") == 0
        assert safe_int(None) == 0
