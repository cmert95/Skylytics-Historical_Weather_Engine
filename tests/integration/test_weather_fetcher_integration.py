import json

from src import config, weather_data_fetcher


def test_weather_fetch_real(tmp_path, monkeypatch):
    """
    Full integration test:
    - Real API call to Open-Meteo
    - Real file writing
    - Simulated location file input
    """

    fake_location = {"latitude": 52.52, "longitude": 13.405, "postal": "69115"}
    location_path = tmp_path / "location.json"
    with open(location_path, "w", encoding="utf-8") as f:
        json.dump(fake_location, f)

    raw_data_dir = tmp_path / "weather_data"
    raw_data_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(config, "SYSTEM_LOCATION_PATH", str(location_path))
    monkeypatch.setattr(config, "RAW_DATA_DIR", raw_data_dir)

    monkeypatch.setattr(weather_data_fetcher, "SYSTEM_LOCATION_PATH", str(location_path))
    monkeypatch.setattr(weather_data_fetcher, "RAW_DATA_DIR", raw_data_dir)

    success = weather_data_fetcher.run()
    assert success is True

    files = list(raw_data_dir.glob("*.json"))
    assert len(files) == 1

    with open(files[0], "r", encoding="utf-8") as f:
        data = json.load(f)
        assert "daily" in data
        assert "time" in data["daily"]
