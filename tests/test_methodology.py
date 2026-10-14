from app import app


def test_methodology_page_loads():
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.get("/methodology")

    assert response.status_code == 200
    assert b"Detection Methodology" in response.data
    assert b"URL Detection Rules" in response.data
    assert b"Email Detection Rules" in response.data
    assert b"Limitations and Safe Use" in response.data


def test_methodology_page_has_navigation():
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.get("/methodology")

    assert b'href="/history"' in response.data
    assert b'href="/url-analyzer"' in response.data
    assert b'href="/email-analyzer"' in response.data
