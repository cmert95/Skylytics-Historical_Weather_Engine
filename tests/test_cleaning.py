from src import cleaning
import pandas as pd


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
