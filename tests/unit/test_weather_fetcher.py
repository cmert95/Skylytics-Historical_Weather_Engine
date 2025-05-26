import json
from datetime import date, timedelta
from unittest.mock import Mock, mock_open, patch

import requests

from src import weather_data_fetcher as wdf


class TestGetLocationInfo:
    def test_valid_location_file(self, tmp_path, caplog):
        loc = {"latitude": 52.52, "longitude": 13.405, "postal": "69115"}
        file_path = tmp_path / "loc.json"
        file_path.write_text(json.dumps(loc))

        lat, lon, postal = wdf.get_location_info(str(file_path))
        assert (lat, lon, postal) == (52.52, 13.405, "69115")
        assert "[CONFIG] Location info loaded" in caplog.text

    def test_missing_file(self, tmp_path, caplog):
        file_path = tmp_path / "nonexistent.json"
        lat, lon, postal = wdf.get_location_info(str(file_path))
        assert (lat, lon, postal) == (None, None, None)
        assert "[CONFIG] File system error" in caplog.text

    def test_invalid_json(self, tmp_path, caplog):
        file_path = tmp_path / "bad.json"
        file_path.write_text("{ bad json }")

        lat, lon, postal = wdf.get_location_info(str(file_path))
        assert (lat, lon, postal) == (None, None, None)
        assert "[CONFIG] Malformed JSON" in caplog.text

    def test_missing_fields(self, tmp_path, caplog):
        loc = {"latitude": 52.52}
        file_path = tmp_path / "partial.json"
        file_path.write_text(json.dumps(loc))

        lat, lon, postal = wdf.get_location_info(str(file_path))
        assert (lat, lon, postal) == (None, None, None)
        assert "[CONFIG] Logical validation failed" in caplog.text


class TestGetWeatherData:
    @patch("src.weather_data_fetcher.requests.get")
    def test_successful_fetch(self, mock_get, caplog):
        mock_resp = Mock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"daily": {"temperature_2m_max": [20]}}
        mock_get.return_value = mock_resp

        data = wdf.get_weather_data(52.52, 13.405, "2023-01-01", "2023-01-05")
        assert data == {"daily": {"temperature_2m_max": [20]}}
        assert "[FETCH] Data fetched successfully" in caplog.text

    @patch("src.weather_data_fetcher.requests.get")
    def test_http_error(self, mock_get, caplog):
        mock_resp = Mock()
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=Mock(status_code=500, text="Internal Server Error")
        )
        mock_get.return_value = mock_resp

        data = wdf.get_weather_data(0, 0, "2023-01-01", "2023-01-05")
        assert data is None
        assert "[FETCH] HTTP error" in caplog.text

    @patch("src.weather_data_fetcher.requests.get")
    def test_timeout_error(self, mock_get, caplog):
        mock_get.side_effect = requests.exceptions.Timeout("timeout")
        data = wdf.get_weather_data(0, 0, "2023-01-01", "2023-01-05")
        assert data is None
        assert "[FETCH] Network error during request" in caplog.text


class TestSaveToFile:
    def test_successful_save(self, tmp_path, caplog):
        file_path = tmp_path / "data.json"
        data = {"weather": "sunny"}

        result = wdf.save_to_file(data, str(file_path))
        assert result is True
        assert file_path.exists()
        assert json.loads(file_path.read_text()) == data
        assert "[SAVE] Weather data saved to" in caplog.text

    @patch("builtins.open", new_callable=mock_open)
    def test_permission_error(self, mock_file, caplog):
        mock_file.side_effect = PermissionError("Denied")
        result = wdf.save_to_file({"x": 1}, "dummy.json")
        assert result is False
        assert "[SAVE] File system error" in caplog.text

    @patch("json.dump")
    @patch("builtins.open", new_callable=mock_open)
    def test_serialization_error(self, mock_file, mock_json_dump, caplog):
        mock_json_dump.side_effect = TypeError("bad type")
        result = wdf.save_to_file({"bad": set()}, "dummy.json")
        assert result is False
        assert "[SAVE] Serialization error" in caplog.text


class TestPrepareDateRange:
    def test_correct_range(self):
        today = date.today()
        start_expected = today - timedelta(days=wdf.DAYS_TO_PULL)
        start, end = wdf.prepare_date_range()
        assert start == start_expected.isoformat()
        assert end == today.isoformat()
