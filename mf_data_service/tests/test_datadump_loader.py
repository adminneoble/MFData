"""Unit tests for the datadump file parser (no MongoDB needed)."""

import os
import json
import tempfile
import pytest

from app.services.datadump_loader import parse_datadump_file


def _write_temp_file(content: str) -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    f.write(content)
    f.close()
    return f.name


class TestParseDatadumpFile:
    def test_parse_standard_format(self):
        content = json.dumps({"Table": [
            {"schemecode": "1", "name": "Scheme A"},
            {"schemecode": "2", "name": "Scheme B"},
            {"schemecode": "3", "name": "Scheme C"},
        ]})
        path = _write_temp_file(content)
        try:
            records = parse_datadump_file(path)
            assert len(records) == 3
            assert records[0]["schemecode"] == "1"
            assert records[2]["name"] == "Scheme C"
        finally:
            os.unlink(path)

    def test_parse_multiline_format(self):
        """Tests the real data format: first line has {"Table":[{...}, subsequent lines start with ,{...}"""
        lines = [
            '{"Table":[{"schemecode":"1","name":"A"}',
            ',{"schemecode":"2","name":"B"}',
            ',{"schemecode":"3","name":"C"}]}',
        ]
        path = _write_temp_file("\n".join(lines))
        try:
            records = parse_datadump_file(path)
            assert len(records) == 3
            assert records[1]["schemecode"] == "2"
        finally:
            os.unlink(path)

    def test_parse_empty_file(self):
        path = _write_temp_file("")
        try:
            records = parse_datadump_file(path)
            assert records == []
        finally:
            os.unlink(path)

    def test_parse_missing_file(self):
        records = parse_datadump_file("/nonexistent/path.txt")
        assert records == []

    def test_parse_real_scheme_master(self):
        path = os.path.join(
            os.environ.get("DATADUMP_ROOT", "/Users/jpsinha/Documents/MFDataService"),
            "Scheme_master.txt",
        )
        if not os.path.exists(path):
            pytest.skip("Scheme_master.txt not found")
        records = parse_datadump_file(path)
        assert len(records) > 10000
        assert "schemecode" in records[0]
        assert "scheme_name" in records[0]

    def test_parse_real_schemeisin(self):
        path = os.path.join(
            os.environ.get("DATADUMP_ROOT", "/Users/jpsinha/Documents/MFDataService"),
            "schemeisinmaster.txt",
        )
        if not os.path.exists(path):
            pytest.skip("schemeisinmaster.txt not found")
        records = parse_datadump_file(path)
        assert len(records) > 10000
        assert "ISIN" in records[0]
        assert records[0]["ISIN"].startswith("IN")
