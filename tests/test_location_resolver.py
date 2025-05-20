from src import location_resolver as lr


class TestLocationResolver:

    def test_save_and_read_location(self, tmp_path):
        location = {
            "city": "Heidelberg",
            "postal": "69115",
            "latitude": 52.505,
            "longitude": 13.405,
        }
        test_file = tmp_path / "loc.json"
        lr.save_location(location, path=test_file)
        assert test_file.exists()

        loaded = lr.read_location_file(test_file)
        assert loaded == location

    def test_save_location_none(self, tmp_path, caplog):
        path = tmp_path / "none.json"
        lr.save_location(None, path=path)
        assert "[SAVE] No location information provided." in caplog.text
        assert not path.exists()

    def test_read_location_file_not_found(self, tmp_path, caplog):
        path = tmp_path / "does_not_exist.json"
        result = lr.read_location_file(path)
        assert result is None
        assert "[CONFIG] Failed to read location file" in caplog.text

    def test_fetch_location_from_ip_structure(self):
        result = lr.fetch_location_from_ip()
        if result:
            assert "latitude" in result
            assert "longitude" in result
            assert "postal" in result
