import json
import time

from src import data_cleaner as dc


class TestGetLatestRawFile:
    def test_returns_latest_file(self, tmp_path, caplog):
        f1 = tmp_path / "raw_weather_20240101.json"
        f2 = tmp_path / "raw_weather_20240102.json"

        f1.write_text("{}")
        time.sleep(0.1)
        f2.write_text("{}")

        latest = dc.get_latest_raw_file(tmp_path)

        assert latest.name == f2.name
        assert "[FILE] Latest raw file selected" in caplog.text

    def test_no_files_found(self, tmp_path, caplog):
        result = dc.get_latest_raw_file(tmp_path)
        assert result is None
        assert "[FILE] No raw weather files found." in caplog.text


class TestLoadLocationInfo:
    def test_valid_location_file(self, tmp_path, caplog):
        data = {"city": "Heidelberg", "postal": "69115"}
        f = tmp_path / "loc.json"
        f.write_text(json.dumps(data))

        city, postal = dc.load_location_info(f)
        assert (city, postal) == ("Heidelberg", "69115")
        assert "[CONFIG] Loaded city & postal" in caplog.text

    def test_missing_file(self, tmp_path, caplog):
        fake = tmp_path / "missing.json"
        city, postal = dc.load_location_info(fake)
        assert (city, postal) == (None, None)
        assert "not found" in caplog.text

    def test_invalid_json(self, tmp_path, caplog):
        f = tmp_path / "bad.json"
        f.write_text("{ not: valid }")
        city, postal = dc.load_location_info(f)
        assert (city, postal) == (None, None)
        assert "Invalid JSON" in caplog.text

    def test_missing_fields(self, tmp_path, caplog):
        f = tmp_path / "partial.json"
        f.write_text(json.dumps({"city": "Heidelberg"}))
        city, postal = dc.load_location_info(f)
        assert (city, postal) == (None, None)
        assert "Missing 'city' or 'postal'" in caplog.text


class TestLoadRawWeather:
    def test_valid_file(self, tmp_path, caplog):
        data = {"daily": {"time": ["2023-01-01"]}}
        f = tmp_path / "weather.json"
        f.write_text(json.dumps(data))
        result = dc.load_raw_weather(f)
        assert result == data
        assert "[LOAD] Raw weather data loaded" in caplog.text

    def test_missing_file(self, tmp_path, caplog):
        f = tmp_path / "missing.json"
        result = dc.load_raw_weather(f)
        assert result is None
        assert "does not exist" in caplog.text

    def test_invalid_json(self, tmp_path, caplog):
        f = tmp_path / "bad.json"
        f.write_text("{ invalid }")
        result = dc.load_raw_weather(f)
        assert result is None
        assert "Invalid JSON" in caplog.text
