import json

from src import config, location_resolver


def test_resolve_location_real(tmp_path, monkeypatch):
    """
    Full integration test:
    - Real IP API call
    - Real file writing
    - Uses consistent SYSTEM_LOCATION_PATH logic
    """

    fake_location_path = tmp_path / "location.json"

    monkeypatch.setattr(config, "SYSTEM_LOCATION_PATH", fake_location_path)
    monkeypatch.setattr(location_resolver, "SYSTEM_LOCATION_PATH", fake_location_path)

    result = location_resolver.resolve_location()
    assert result is not None
    assert all(k in result for k in ("city", "postal", "latitude", "longitude"))

    success = location_resolver.save_location(result, path=fake_location_path)
    assert success
    assert fake_location_path.exists()

    with open(fake_location_path, "r", encoding="utf-8") as f:
        saved = json.load(f)
        assert saved == result
