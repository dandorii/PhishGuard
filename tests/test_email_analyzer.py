import pytest

from analyzers.email_analyzer import analyze_email


def test_plain_email_has_no_indicators():
    result = analyze_email(
        "Hello, the meeting is scheduled for tomorrow."
    )

    assert result["score"] == 0
    assert result["severity"] == "Low"
    assert result["indicators"] == []


def test_urgency_language_is_detected():
    result = analyze_email(
        "Urgent action required. Please review this notice."
    )

    assert any(
        item["rule"] == "urgency_language"
        for item in result["indicators"]
    )


def test_credential_request_is_detected():
    result = analyze_email(
        "Please enter your password to verify your account."
    )

    rules = [item["rule"] for item in result["indicators"]]

    assert "credential_request" in rules
    assert "urgency_language" in rules


def test_financial_request_is_detected():
    result = analyze_email(
        "Please send gift cards to complete this request."
    )

    assert any(
        item["rule"] == "financial_request"
        for item in result["indicators"]
    )


def test_url_presence_is_detected():
    result = analyze_email(
        "Please review this link: https://example.com"
    )

    assert any(
        item["rule"] == "contains_url"
        for item in result["indicators"]
    )


@pytest.mark.parametrize(
    "email",
    [
        "",
        "   ",
        None,
        123,
    ],
)
def test_invalid_email_input_is_rejected(email):
    with pytest.raises(ValueError):
        analyze_email(email)


def test_email_length_limit():
    with pytest.raises(ValueError):
        analyze_email("a" * 20001)


def test_score_is_bounded():
    result = analyze_email(
        "Urgent action required. "
        "Please enter your password. "
        "Send gift cards. "
        "https://example.com"
    )

    assert 0 <= result["score"] <= 100
