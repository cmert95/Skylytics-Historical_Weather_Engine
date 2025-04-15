from src import ip


# Check if IP info is returned or handled safely
def test_get_ip_info():
    result = ip.get_ip_info()
    assert result is None or ("city" in result and "postal" in result)


# Save valid location and check if file is created
def test_save_location_success(tmp_path):
    location = {"city": "Heidelberg", "postal": "69115"}
    test_file = tmp_path / "test_location.json"
    ip.save_location(location, filename=str(test_file))
    assert test_file.exists()


# Saving empty dict should not create a file
def test_save_location_empty_dict(tmp_path):
    file_path = tmp_path / "empty.json"
    ip.save_location({}, filename=str(file_path))
    assert not file_path.exists()


# Saving None should not create a file
def test_save_location_none_file_not_created(tmp_path):
    file_path = tmp_path / "dummy.json"
    ip.save_location(None, filename=str(file_path))
    assert not file_path.exists()


# Check if warning log is written when input is None
def test_save_location_none_logs_warning(tmp_path, caplog):
    ip.save_location(None, filename=str(tmp_path / "logcheck.json"))
    assert "No location information provided" in caplog.text
