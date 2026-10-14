import re

import pytest

from app import app


PAGES = [
    ("/", "dashboard"),
    ("/url-analyzer", "url"),
    ("/email-analyzer", "email"),
    ("/history", "history"),
    ("/methodology", "methodology"),
]

NAV_HREFS = [
    "/",
    "/url-analyzer",
    "/email-analyzer",
    "/history",
    "/methodology",
]


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


@pytest.mark.parametrize("path, _key", PAGES)
def test_every_page_has_shared_navigation(client, path, _key):
    html = client.get(path).get_data(as_text=True)

    assert 'id="site-sidebar"' in html
    assert 'id="site-nav"' in html
    assert 'id="nav-toggle"' in html

    for href in NAV_HREFS:
        assert f'href="{href}"' in html


@pytest.mark.parametrize("path, _key", PAGES)
def test_menu_button_is_wired_to_navigation(client, path, _key):
    html = client.get(path).get_data(as_text=True)

    # The toggle must control the nav and start collapsed.
    assert 'aria-controls="site-nav"' in html
    assert 'aria-expanded="false"' in html
    assert "Menu" in html


@pytest.mark.parametrize("path, _key", PAGES)
def test_only_current_page_is_marked_active(client, path, _key):
    html = client.get(path).get_data(as_text=True)

    assert len(re.findall(r'aria-current="page"', html)) == 1

    active_link = re.search(
        r'class="nav-link active"\s+href="([^"]+)"\s+aria-current="page"',
        html,
    )

    assert active_link is not None
    assert active_link.group(1) == path
