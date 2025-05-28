import json

import pandas as pd

from src import config, data_cleaner


def test_data_cleaning_real(tmp_path, monkeypatch):
    """
    Full integration test for data_cleaner:
    - Uses real file I/O
    - Simulates raw weather data and location file
    - Verifies cleaned CSV output
    """

    fake_location = {"city": "Berlin", "postal": "10115"}
    location_path = tmp_path / "location.json"
    with open(location_path, "w", encoding="utf-8") as f:
        json.dump(fake_location, f)

    fake_raw = {
        "daily": {
            "time": ["2023-01-01", "2023-01-02"],
            "temperature_2m_max": [5.0, 6.0],
            "temperature_2m_min": [-1.0, 0.0],
            "temperature_2m_mean": [2.0, 3.0],
            "precipitation_sum": [1.2, 0.8],
            "rain_sum": [1.0, 0.5],
            "snowfall_sum": [0.2, 0.3],
            "windspeed_10m_max": [10.0, 12.0],
            "shortwave_radiation_sum": [3.5, 3.6],
            "sunshine_duration": [120, 150],
        }
    }
    raw_data_dir = tmp_path / "raw"
    raw_data_dir.mkdir()
    raw_file_path = raw_data_dir / "raw_weather_10115_sample.json"
    with open(raw_file_path, "w", encoding="utf-8") as f:
        json.dump(fake_raw, f)

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()

    monkeypatch.setattr(config, "RAW_DATA_DIR", raw_data_dir)
    monkeypatch.setattr(config, "STAGING_DATA_DIR", staging_dir)
    monkeypatch.setattr(config, "SYSTEM_LOCATION_PATH", location_path)

    monkeypatch.setattr(data_cleaner, "RAW_DATA_DIR", raw_data_dir)
    monkeypatch.setattr(data_cleaner, "STAGING_DATA_DIR", staging_dir)
    monkeypatch.setattr(data_cleaner, "SYSTEM_LOCATION_PATH", location_path)

    success = data_cleaner.run()
    assert success is True

    csv_files = list(staging_dir.glob("*.csv"))
    assert len(csv_files) == 1

    df = pd.read_csv(csv_files[0])
    assert not df.empty
    assert "Date" in df.columns
    assert "Temp_Max_C" in df.columns
    assert df["City"].iloc[0] == "Berlin"
