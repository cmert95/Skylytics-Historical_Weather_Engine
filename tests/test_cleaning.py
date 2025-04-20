import pandas as pd

from src import cleaning


# Tests if cleaning function works properly
def test_clean_data_sample():
    raw_data = {
        "forecast": {
            "forecastday": [
                {
                    "hour": [
                        {
                            "time": "2025-04-15 12:00",
                            "temp_c": 20,
                            "condition": {"text": "Sunny"},
                            "humidity": 40,
                            "wind_kph": 10,
                            "feelslike_c": 20,
                        }
                    ]
                }
            ]
        }
    }
    df = cleaning.clean_data(raw_data, "Berlin", "69115")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "Temperature_C" in df.columns


# Test when empty raw data returns empty DataFrame
def test_clean_data_empty():
    df = cleaning.clean_data({}, "City", "00000")
    assert isinstance(df, pd.DataFrame)
    assert df.empty


# Test when invalid raw JSON file
def test_load_raw_data_invalid(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{invalid_json")
    result = cleaning.load_raw_data(str(bad_file))
    assert result is None


# Test: find_latest_file returns correct path
def test_find_latest_file(tmp_path, monkeypatch):
    from src import cleaning

    f1 = tmp_path / "raw_weather_1.json"
    f2 = tmp_path / "raw_weather_2.json"
    f1.write_text("{}")
    f2.write_text("{}")

    def fake_getctime(path):
        return 100 if "2" in path else 50

    monkeypatch.setattr("os.path.getctime", fake_getctime)

    latest = cleaning.find_latest_file(path=str(tmp_path))

    assert latest.endswith("raw_weather_2.json")


# Test: get_location_info returns correct city and postal
def test_get_location_info(tmp_path):
    file = tmp_path / "location.json"
    file.write_text('{"city": "Heidelberg", "postal": "69115"}')

    from src import cleaning

    city, postal = cleaning.get_location_info(filename=str(file))

    assert city == "Heidelberg"
    assert postal == "69115"


# Test: get_location_info handles missing file
def test_get_location_info_file_missing():
    from src import cleaning

    city, postal = cleaning.get_location_info(filename="nonexistent.json")
    assert city is None and postal is None


# Test: get_location_info handles invalid JSON
def test_get_location_info_invalid_json(tmp_path):
    file = tmp_path / "broken.json"
    file.write_text("{ invalid json }")

    from src import cleaning

    city, postal = cleaning.get_location_info(filename=str(file))
    assert city is None and postal is None
