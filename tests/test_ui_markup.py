import pytest

from app import app


PAGES = ["/", "/url-analyzer", "/email-analyzer", "/history", "/methodology"]


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def test_favicon_is_served_as_svg(client):
    response = client.get("/static/favicon.svg")

    assert response.status_code == 200
    assert response.mimetype == "image/svg+xml"
    assert b"<svg" in response.data


@pytest.mark.parametrize("path", PAGES)
def test_every_page_links_the_favicon(client, path):
    html = client.get(path).get_data(as_text=True)

    assert 'rel="icon"' in html
    assert "favicon.svg" in html


@pytest.mark.parametrize("path", PAGES)
def test_every_page_has_live_status_element(client, path):
    html = client.get(path).get_data(as_text=True)

    assert 'id="system-status"' in html
    # The static "online" label must not be hardcoded in the markup.
    assert "SYSTEM ONLINE</span>" not in html


@pytest.mark.parametrize("path", PAGES)
def test_misleading_development_label_is_removed(client, path):
    html = client.get(path).get_data(as_text=True)

    assert "Development Mode" not in html
    assert "Educational demo" in html


def test_history_page_has_themed_confirmation_dialog(client):
    html = client.get("/history").get_data(as_text=True)

    assert '<dialog class="confirm-dialog" id="confirm-dialog"' in html
    assert 'aria-labelledby="confirm-title"' in html
    assert 'value="confirm"' in html


def test_methodology_critical_badge_uses_critical_style(client):
    html = client.get("/methodology").get_data(as_text=True)

    assert '<span class="risk critical">Critical</span>' in html
    assert '<span class="risk high">Critical</span>' not in html


def test_index_has_no_stray_markdown_fence(client):
    html = client.get("/").get_data(as_text=True)

    assert "```" not in html
