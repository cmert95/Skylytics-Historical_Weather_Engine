from src import ip


# Checks if IP info is retrieved correctly
def test_get_ip_info():
    result = ip.get_ip_info()
    assert result is None or ("city" in result and "postal" in result)


# Should NOT create file when location is empty
def test_save_empty_location(tmp_path):
    file_path = tmp_path / "empty.json"
    ip.save_location({}, filename=str(file_path))
    assert not file_path.exists()


# Checks saving None does not crash
def test_save_location_none(tmp_path):
    ip.save_location(None, filename=str(tmp_path / "dummy.json"))
    assert (tmp_path / "dummy.json").exists() is False
