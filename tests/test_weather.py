from src import weather
import json


# Check that API key is retrieved from environment
def test_api_key_exists(monkeypatch):
    monkeypatch.setenv("API_KEY", "fake-key")
    assert weather.get_api_key() == "fake-key"


# Test when JSON config missing
def test_get_infos_from_missing_file():
    city, postal = weather.get_infos_from_json("non_existent.json")
    assert city is None and postal is None


# Return (city, postal) from valid JSON
def test_get_infos_from_json(tmp_path):
    file = tmp_path / "location.json"
    file.write_text(json.dumps({"city": "Berlin", "postal": "10115"}))
    city, postal = weather.get_infos_from_json(filename=str(file))
    assert city == "Berlin" and postal == "10115"


# Test: Broken JSON returns (None, None)
def test_get_infos_from_invalid_json(tmp_path):
    file = tmp_path / "broken.json"
    file.write_text("{ invalid json }")
    city, postal = weather.get_infos_from_json(filename=str(file))
    assert city is None and postal is None


# Test: API key is empty string
def test_api_key_empty(monkeypatch):
    monkeypatch.setenv("API_KEY", "")
    assert weather.get_api_key() is None


# Test: get_forecast returns None for empty city
def test_get_forecast_empty_city():
    result = weather.get_forecast("", "fake-key")
    assert result is None


# Test: save_forecast_to_json exits if forecast is None
def test_save_forecast_to_json_none(monkeypatch):
    monkeypatch.setattr(weather, "get_infos_from_json", lambda *_: ("abc", "123"))
    monkeypatch.setattr(weather, "get_api_key", lambda: "fake-key")
    monkeypatch.setattr(weather, "get_forecast", lambda *_: None)

    result = weather.save_forecast_to_json()
    assert result is None
