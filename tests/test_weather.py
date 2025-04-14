from src import weather


# Verifies that the API key exists
def test_api_key_exists():
    api_key = weather.get_api_key()
    assert api_key is not None and len(api_key) > 0


# Test when JSON config missing
def test_get_infos_from_missing_file():
    city, postal = weather.get_infos_from_json("non_existent.json")
    assert city is None and postal is None
