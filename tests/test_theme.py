import pytest

from app import app


PAGES = ["/", "/url-analyzer", "/email-analyzer", "/history", "/methodology"]


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


@pytest.mark.parametrize("path", PAGES)
def test_every_page_has_theme_toggle(client, path):
    html = client.get(path).get_data(as_text=True)

    assert 'id="theme-toggle"' in html
    assert 'class="theme-toggle"' in html


@pytest.mark.parametrize("path", PAGES)
def test_theme_script_runs_before_stylesheet(client, path):
    html = client.get(path).get_data(as_text=True)

    script_index = html.index("phishguard-theme")
    stylesheet_index = html.index("css/style.css")

    # The saved theme must be applied before the stylesheet loads.
    assert script_index < stylesheet_index


def test_stylesheet_defines_light_and_dark_tokens(client):
    css = client.get("/static/css/style.css").get_data(as_text=True)

    assert ":root {" in css
    assert ':root[data-theme="light"]' in css
    assert "@media (prefers-color-scheme: light)" in css
    assert 'color-scheme: dark' in css
    assert 'color-scheme: light' in css
