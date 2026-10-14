
from ipaddress import ip_address
from urllib.parse import urlsplit


MAX_URL_LENGTH = 2048


def analyze_url(raw_url):
    """
    Inspect URL structure without visiting the website.

    Returns explainable indicators and a heuristic risk score.
    The score is not a probability of phishing.
    """

    if not isinstance(raw_url, str):
        raise ValueError("URL must be provided as text.")

    url = raw_url.strip()

    if not url:
        raise ValueError("Please enter a URL.")

    if len(url) > MAX_URL_LENGTH:
        raise ValueError("URL exceeds the maximum allowed length.")

    if any(character.isspace() or ord(character) < 32 for character in url):
        raise ValueError("URL contains whitespace or control characters.")

    try:
        parsed = urlsplit(url)

        # Accessing hostname and port can raise ValueError
        # when the URL contains malformed authority information.
        scheme = parsed.scheme.lower()
        hostname = parsed.hostname
        parsed.port

    except ValueError:
        raise ValueError("The URL format is invalid.") from None

    if scheme not in {"http", "https"}:
        raise ValueError("Only HTTP and HTTPS URLs are supported.")

    if not parsed.netloc or not hostname:
        raise ValueError("The URL must include a hostname.")

    hostname = hostname.lower().rstrip(".")

    if not hostname:
        raise ValueError("The hostname is invalid.")

    indicators = []
    score = 0

    def add_indicator(rule, points, explanation):
        nonlocal score

        indicators.append({
            "rule": rule,
            "points": points,
            "explanation": explanation,
        })

        score += points

    # Rule 1: Plain HTTP
    if scheme == "http":
        add_indicator(
            "plain_http",
            15,
            "The URL uses HTTP rather than encrypted HTTPS.",
        )

    # Rule 2: IP address used as the hostname
    try:
        ip_address(hostname)
        is_ip_address = True
    except ValueError:
        is_ip_address = False

    if is_ip_address:
        add_indicator(
            "ip_address_host",
            25,
            "The hostname is an IP address instead of a domain name.",
        )

    # Rule 3: Embedded credentials or an @ sign in the authority
    if "@" in parsed.netloc:
        add_indicator(
            "at_symbol",
            20,
            "The URL contains an @ symbol in its authority, "
            "which can obscure the intended destination.",
        )

    # Rule 4: Unusually long hostname
    if len(hostname) > 50:
        add_indicator(
            "long_hostname",
            10,
            "The hostname is unusually long.",
        )

    # Rule 5: Many hostname labels
    if not is_ip_address and len(hostname.split(".")) > 4:
        add_indicator(
            "many_subdomains",
            15,
            "The hostname contains many dot-separated labels.",
        )

    # Rule 6: Internationalized or Unicode hostname
    if not hostname.isascii():
        add_indicator(
            "unicode_hostname",
            20,
            "The hostname contains non-ASCII characters. "
            "Check carefully for look-alike characters.",
        )

    # Rule 7: Explicit punycode label
    if any(
        label.startswith("xn--")
        for label in hostname.split(".")
    ):
        add_indicator(
            "punycode_hostname",
            10,
            "The hostname contains a punycode label.",
        )

    # Bound the heuristic score to 0–100.
    score = min(score, 100)

    if score >= 80:
        severity = "Critical"
    elif score >= 60:
        severity = "High"
    elif score >= 30:
        severity = "Medium"
    else:
        severity = "Low"

    return {
        "score": score,
        "severity": severity,
        "indicators": indicators,
        "indicator_count": len(indicators),
        "message": (
            "Indicators were found. Review the findings carefully."
            if indicators
            else "No configured structural indicators were detected."
        ),
    }
