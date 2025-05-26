import json

from src import weather_data_fetcher as wdf


class TestGetLocationInfo:
    def test_valid_location_file(self, tmp_path):
        file = tmp_path / "loc.json"
        file.write_text(json.dumps({"latitude": 52.52, "longitude": 13.405, "postal": "69115"}))

        lat, lon, postal = wdf.get_location_info(filename=str(file))
        assert lat == 52.52
        assert lon == 13.405
        assert postal == "69115"

    def test_missing_file(self):
        lat, lon, postal = wdf.get_location_info(filename="non_existent.json")
        assert lat is None and lon is None and postal is None

    def test_invalid_json(self, tmp_path):
        file = tmp_path / "broken.json"
        file.write_text("{ invalid json }")
        lat, lon, postal = wdf.get_location_info(filename=str(file))
        assert lat is None and lon is None and postal is None

    def test_missing_fields(self, tmp_path):
        file = tmp_path / "partial.json"
        file.write_text(json.dumps({"latitude": 52.52}))
        lat, lon, postal = wdf.get_location_info(filename=str(file))
        assert lat is None and lon is None and postal is None
