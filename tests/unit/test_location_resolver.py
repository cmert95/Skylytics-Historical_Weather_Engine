import json
from unittest.mock import Mock, mock_open, patch

import requests

from src import location_resolver as lr


class TestFetchLocationFromIP:
    @patch("src.location_resolver.requests.get")
    def test_successful_fetch(self, mock_get, caplog):
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
        assert "[FETCH] Location fetched from IP" in caplog.text

    @patch("src.location_resolver.requests.get")
    def test_fetch_timeout(self, mock_get, caplog):
        mock_get.side_effect = requests.exceptions.Timeout
        result = lr.fetch_location_from_ip()
        assert result is None
        assert "[FETCH] API request failed" in caplog.text

    @patch("src.location_resolver.requests.get")
    def test_incomplete_response(self, mock_get, caplog):
        mock_response = Mock()
        mock_response.json.return_value = {
            "city": "Heidelberg",
            "postal": "69115",
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = lr.fetch_location_from_ip()
        assert result is None
        assert "[FETCH] Incomplete location info from IP API" in caplog.text

    @patch("src.location_resolver.requests.get")
    def test_malformed_coordinates(self, mock_get, caplog):
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
        assert "[FETCH] Failed to parse coordinates" in caplog.text


class TestSaveLocation:
    def test_save_valid_location(self, tmp_path, caplog):
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
        assert "[SAVE] Location saved to" in caplog.text

    def test_save_location_none(self, tmp_path, caplog):
        path = tmp_path / "none.json"
        result = lr.save_location(None, path=path)
        assert result is False
        assert not path.exists()
        assert "[SAVE] No location information provided." in caplog.text

    @patch("builtins.open", new_callable=mock_open)
    def test_save_raises_permission_error(self, mock_file, caplog):
        mock_file.side_effect = PermissionError("No permission")
        location = {
            "city": "Heidelberg",
            "postal": "69115",
            "latitude": 52.52,
            "longitude": 13.405,
        }
        result = lr.save_location(location, path="fake_path.json")
        assert result is False
        assert "[SAVE] File system error while saving" in caplog.text
        assert "No permission" in caplog.text

    @patch("json.dump")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_invalid_data(self, mock_file, mock_json_dump, caplog):
        mock_json_dump.side_effect = TypeError("Data not serializable")

        data = {"city": "Heidelberg", "bad": set()}
        result = lr.save_location(data, path="file.json")

        assert result is False
        assert "[SAVE] Data format issue" in caplog.text
        assert "Data not serializable" in caplog.text


class TestReadLocationFile:
    def test_read_valid_location(self, tmp_path, caplog):
        location = {
            "city": "Heidelberg",
            "postal": "69115",
            "latitude": 52.52,
            "longitude": 13.405,
        }
        file_path = tmp_path / "loc.json"
        file_path.write_text(json.dumps(location))

        result = lr.read_location_file(file_path)
        assert result == location

    def test_file_not_found(self, tmp_path, caplog):
        fake_path = tmp_path / "missing.json"
        result = lr.read_location_file(fake_path)
        assert result is None
        assert "[CONFIG] Location file not found" in caplog.text

    def test_invalid_json(self, tmp_path, caplog):
        file_path = tmp_path / "invalid.json"
        file_path.write_text("{ not: valid json }")

        result = lr.read_location_file(file_path)
        assert result is None
        assert "[CONFIG] Invalid JSON format" in caplog.text

    @patch("builtins.open", new_callable=mock_open)
    def test_permission_error(self, mock_file, caplog):
        mock_file.side_effect = PermissionError("Access denied")
        result = lr.read_location_file("dummy.json")
        assert result is None
        assert "[CONFIG] Location file not found" in caplog.text
        assert "Access denied" in caplog.text

    @patch("builtins.open", new_callable=mock_open)
    def test_unexpected_os_error(self, mock_file, caplog):
        mock_file.side_effect = OSError("Some OS error")
        result = lr.read_location_file("dummy.json")
        assert result is None
        assert "[CONFIG] Error reading file" in caplog.text
        assert "Some OS error" in caplog.text


class TestResolveLocation:
    @patch(
        "src.location_resolver.SETTINGS",
        {"location": {"latitude": 1.0, "longitude": 2.0, "postal": "12345", "city": "Ankara"}},
    )
    def test_resolve_from_settings(self, caplog):
        result = lr.resolve_location()
        assert result == {
            "latitude": 1.0,
            "longitude": 2.0,
            "postal": "12345",
            "city": "Ankara",
        }
        assert "[CONFIG] Location loaded from settings.yaml" in caplog.text

    @patch("src.location_resolver.SETTINGS", {"location": {}})
    @patch("src.location_resolver.Path.exists", return_value=True)
    @patch("src.location_resolver.read_location_file")
    def test_resolve_from_cached_file(self, mock_read, mock_exists, caplog):
        mock_read.return_value = {
            "latitude": 3.0,
            "longitude": 4.0,
            "postal": "67890",
            "city": "Berlin",
        }
        result = lr.resolve_location()
        assert result == mock_read.return_value
        assert "[CONFIG] Using cached location from disk" in caplog.text

    @patch("src.location_resolver.SETTINGS", {"location": {}})
    @patch("src.location_resolver.Path.exists", return_value=False)
    @patch("src.location_resolver.fetch_location_from_ip")
    @patch("src.location_resolver.save_location")
    def test_resolve_fallback_to_ip(self, mock_save, mock_fetch, mock_exists, caplog):
        mock_fetch.return_value = {
            "latitude": 52.52,
            "longitude": 13.405,
            "postal": "69115",
            "city": "Heidelberg",
        }
        result = lr.resolve_location()
        assert result == mock_fetch.return_value
        mock_save.assert_called_once_with(mock_fetch.return_value)
        assert "[CONFIG] No config or cache found. Falling back to IP-based location" in caplog.text

    @patch("src.location_resolver.SETTINGS", {"location": {}})
    @patch("src.location_resolver.Path.exists", return_value=False)
    @patch("src.location_resolver.fetch_location_from_ip", return_value=None)
    def test_resolve_returns_none_if_all_fail(self, mock_fetch, mock_exists, caplog):
        result = lr.resolve_location()
        assert result is None
        assert "[CONFIG] No config or cache found. Falling back to IP-based location" in caplog.text
