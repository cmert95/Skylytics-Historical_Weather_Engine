import json

import pytest

from src import weather

# TODO: These tests are temporarily disabled during the refactor process. (May 13, 2025 - Mert)


@pytest.mark.skip(reason="Tests are temporarily disabled during the refactor process.")
class TestWeatherModule:

    def test_api_key_exists(self, monkeypatch):
        monkeypatch.setenv("API_KEY", "fake-key")
        assert weather.get_api_key() == "fake-key"

    def test_get_infos_from_missing_file(self):
        city, postal = weather.get_infos_from_json("non_existent.json")
        assert city is None and postal is None

    def test_get_infos_from_json(self, tmp_path):
        file = tmp_path / "location.json"
        file.write_text(json.dumps({"city": "Berlin", "postal": "10115"}))
        city, postal = weather.get_infos_from_json(filename=str(file))
        assert city == "Berlin" and postal == "10115"

    def test_get_infos_from_invalid_json(self, tmp_path):
        file = tmp_path / "broken.json"
        file.write_text("{ invalid json }")
        city, postal = weather.get_infos_from_json(filename=str(file))
        assert city is None and postal is None

    def test_api_key_empty(self, monkeypatch):
        monkeypatch.setenv("API_KEY", "")
        assert weather.get_api_key() is None

    def test_get_forecast_empty_city(self):
        result = weather.get_forecast("", "fake-key")
        assert result is None

    def test_save_forecast_to_json_none(self, monkeypatch):
        monkeypatch.setattr(weather, "get_infos_from_json", lambda *_: ("abc", "123"))
        monkeypatch.setattr(weather, "get_api_key", lambda: "fake-key")
        monkeypatch.setattr(weather, "get_forecast", lambda *_: None)

        result = weather.save_forecast_to_json()
        assert result is None
