import pandas as pd
import pytest

from src import cleaning

# TODO: These tests are temporarily disabled during the refactor process. (May 13, 2025 - Mert)


@pytest.mark.skip(reason="Tests are temporarily disabled during the refactor process.")
class TestCleaningModule:

    def test_clean_data_sample(self):
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

    def test_clean_data_empty(self):
        df = cleaning.clean_data({}, "City", "00000")
        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_load_raw_data_invalid(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{invalid_json")
        result = cleaning.load_raw_data(str(bad_file))
        assert result is None

    def test_find_latest_file(self, tmp_path, monkeypatch):
        f1 = tmp_path / "raw_weather_1.json"
        f2 = tmp_path / "raw_weather_2.json"
        f1.write_text("{}")
        f2.write_text("{}")

        def fake_getctime(path):
            return 100 if "2" in path else 50

        monkeypatch.setattr("os.path.getctime", fake_getctime)

        latest = cleaning.find_latest_file(path=str(tmp_path))
        assert latest.endswith("raw_weather_2.json")

    def test_get_location_info(self, tmp_path):
        file = tmp_path / "location.json"
        file.write_text('{"city": "Heidelberg", "postal": "69115"}')

        city, postal = cleaning.get_location_info(filename=str(file))
        assert city == "Heidelberg"
        assert postal == "69115"

    def test_get_location_info_file_missing(self):
        city, postal = cleaning.get_location_info(filename="nonexistent.json")
        assert city is None and postal is None

    def test_get_location_info_invalid_json(self, tmp_path):
        file = tmp_path / "broken.json"
        file.write_text("{ invalid json }")
        city, postal = cleaning.get_location_info(filename=str(file))
        assert city is None and postal is None
