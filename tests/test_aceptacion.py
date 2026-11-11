from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_units_endpoint_lists_all_categories() -> None:
    response = client.get("/api/units")

    assert response.status_code == 200
    assert len(response.json()) == 8
    assert response.json()["temperatura"]["units"][0]["code"] == "C"


def test_converts_length() -> None:
    response = client.post(
        "/api/convert",
        json={"category": "longitud", "value": 1, "from_unit": "km", "to_unit": "mi"},
    )

    assert response.status_code == 200
    assert abs(response.json()["result"] - 0.621371192237334) < 1e-12


def test_converts_temperature() -> None:
    response = client.post(
        "/api/convert",
        json={"category": "temperatura", "value": 32, "from_unit": "F", "to_unit": "C"},
    )

    assert response.status_code == 200
    assert response.json()["result"] == 0


def test_rejects_units_from_another_category() -> None:
    response = client.post(
        "/api/convert",
        json={"category": "longitud", "value": 1, "from_unit": "km", "to_unit": "kg"},
    )

    assert response.status_code == 422


def test_rejects_non_finite_values() -> None:
    response = client.post(
        "/api/convert",
        json={"category": "longitud", "value": "NaN", "from_unit": "m", "to_unit": "km"},
    )

    assert response.status_code == 422


def test_homepage_is_served() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Conversor de unidades" in response.text


def test_static_stylesheet_is_served() -> None:
    response = client.get("/static/styles.css")

    assert response.status_code == 200
    assert "--green" in response.text
