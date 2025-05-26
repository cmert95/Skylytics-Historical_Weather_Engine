import json
import time
from pathlib import Path

from src import data_cleaner as dc


class TestGetLatestRawFile:
    def test_returns_latest_file(self, tmp_path):
        f1 = tmp_path / "raw_weather_20240101.json"
        f2 = tmp_path / "raw_weather_20240102.json"

        f1.write_text("{}")
        time.sleep(1)
        f2.write_text("{}")

        latest = dc.get_latest_raw_file(tmp_path)
        assert latest.name == f2.name

    def test_returns_none_if_no_files(self, tmp_path):
        result = dc.get_latest_raw_file(tmp_path)
        assert result is None


class TestLoadLocationInfo:
    def test_valid_location_file(self, tmp_path):
        file = tmp_path / "loc.json"
        file.write_text(json.dumps({"city": "Berlin", "postal": "12345"}))

        city, postal = dc.load_location_info(file)
        assert city == "Berlin"
        assert postal == "12345"

    def test_missing_file_returns_none(self):
        file = Path("non_existent.json")
        city, postal = dc.load_location_info(file)
        assert city is None and postal is None

    def test_invalid_json_returns_none(self, tmp_path):
        file = tmp_path / "broken.json"
        file.write_text("{ invalid json }")

        city, postal = dc.load_location_info(file)
        assert city is None and postal is None

    def test_missing_fields_returns_none(self, tmp_path):
        file = tmp_path / "partial.json"
        file.write_text(json.dumps({"city": "Berlin"}))

        city, postal = dc.load_location_info(file)
        assert city is None and postal is None
