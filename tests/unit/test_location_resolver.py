import json
from unittest.mock import Mock, mock_open, patch

import requests

from src import location_resolver as lr


class TestFetchLocationFromIP:
    @patch("src.location_resolver.requests.get")
    def test_successful_fetch(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "city": "Heidelberg",
            "postal": "69115",
            "loc": "52.5200,13.4050",
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = lr.fetch_location_from_ip()
        assert result == {
            "city": "Heidelberg",
            "postal": "69115",
            "latitude": 52.52,
            "longitude": 13.405,
        }

    @patch("src.location_resolver.requests.get")
    def test_fetch_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout
        result = lr.fetch_location_from_ip()
        assert result is None

    @patch("src.location_resolver.requests.get")
    def test_incomplete_response(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "city": "Heidelberg",
            "postal": "69115",
            # missing
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = lr.fetch_location_from_ip()
        assert result is None

    @patch("src.location_resolver.requests.get")
    def test_malformed_coordinates(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "city": "Heidelberg",
            "postal": "69115",
            "loc": "invalid,coord",
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = lr.fetch_location_from_ip()
        assert result is None


class TestSaveLocation:
    def test_save_valid_location(self, tmp_path):
        location = {
            "city": "Heidelberg",
            "postal": "69115",
            "latitude": 52.52,
            "longitude": 13.405,
        }
        file_path = tmp_path / "loc.json"

        result = lr.save_location(location, path=file_path)
        assert result is True
        assert file_path.exists()

        saved = json.loads(file_path.read_text())
        assert saved == location

    def test_save_location_none(self, tmp_path, caplog):
        path = tmp_path / "none.json"
        result = lr.save_location(None, path=path)
        assert result is False
        assert not path.exists()
        assert "[SAVE] No location information provided." in caplog.text

    @patch("builtins.open", new_callable=mock_open)
    def test_save_raises_permission_error(self, mock_file):
        mock_file.side_effect = PermissionError("No permission")
        location = {
            "city": "Heidelberg",
            "postal": "69115",
            "latitude": 52.52,
            "longitude": 13.405,
        }
        result = lr.save_location(location, path="fake_path.json")
        assert result is False

    @patch("builtins.open", new_callable=mock_open)
    def test_save_invalid_data(self, mock_file):
        mock_file.side_effect = TypeError("Data not serializable")
        result = lr.save_location(object(), path="file.json")
        assert result is False
