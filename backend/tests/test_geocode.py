from backend.utils.geocode import geocode_location, enrich_incident


def test_geocode_known_city():
    lat, lon = geocode_location("Mumbai")
    assert lat is not None and lon is not None


def test_enrich_incident_adds_coords():
    inc = {"id": "test-1", "location": "Mumbai", "title": "Test"}
    enriched = enrich_incident(inc)
    assert "lat" in enriched and "lon" in enriched
    assert isinstance(enriched["lat"], float)
    assert isinstance(enriched["lon"], float)
