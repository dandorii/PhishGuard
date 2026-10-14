
import pytest

from analyzers.url_analyzer import analyze_url


def test_https_url_without_indicators():
    result = analyze_url("https://example.com")

    assert result["score"] == 0
    assert result["severity"] == "Low"
    assert result["indicators"] == []


def test_http_url_is_flagged():
    result = analyze_url("http://example.com")

    assert result["score"] == 15
    assert "plain_http" in [
        item["rule"] for item in result["indicators"]
    ]


def test_ip_address_host_is_flagged():
    result = analyze_url("http://192.0.2.1")

    assert "ip_address_host" in [
        item["rule"] for item in result["indicators"]
    ]


def test_at_symbol_is_flagged():
    result = analyze_url("https://trusted.example@evil.example")

    assert "at_symbol" in [
        item["rule"] for item in result["indicators"]
    ]


@pytest.mark.parametrize(
    "url",
    [
        "",
        "   ",
        "ftp://example.com",
        "https:///missing-host",
        "https://example.com/path with spaces",
        "https://[invalid-ip",
    ],
)
def test_invalid_urls_are_rejected(url):
    with pytest.raises(ValueError):
        analyze_url(url)


def test_non_string_input_is_rejected():
    with pytest.raises(ValueError):
        analyze_url(None)


def test_result_has_expected_fields():
    result = analyze_url("http://example.com")

    assert 0 <= result["score"] <= 100
    assert result["severity"] in {
        "Low", "Medium", "High", "Critical"
    }
    assert isinstance(result["indicators"], list)
    assert result["indicator_count"] == len(result["indicators"])
