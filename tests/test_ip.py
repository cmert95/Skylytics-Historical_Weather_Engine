import pytest

from src import ip

# TODO: These tests are temporarily disabled during the refactor process. (May 13, 2025 - Mert)


@pytest.mark.skip(reason="Tests are temporarily disabled during the refactor process.")
class TestIPModule:

    def test_get_ip_info(self):
        result = ip.get_ip_info()
        assert result is None or ("city" in result and "postal" in result)

    def test_save_location_success(self, tmp_path):
        location = {"city": "Heidelberg", "postal": "69115"}
        test_file = tmp_path / "test_location.json"
        ip.save_location(location, filename=str(test_file))
        assert test_file.exists()

    def test_save_location_empty_dict(self, tmp_path):
        file_path = tmp_path / "empty.json"
        ip.save_location({}, filename=str(file_path))
        assert not file_path.exists()

    def test_save_location_none_file_not_created(self, tmp_path):
        file_path = tmp_path / "dummy.json"
        ip.save_location(None, filename=str(file_path))
        assert not file_path.exists()

    def test_save_location_none_logs_warning(self, tmp_path, caplog):
        ip.save_location(None, filename=str(tmp_path / "logcheck.json"))
        assert "No location information provided" in caplog.text
