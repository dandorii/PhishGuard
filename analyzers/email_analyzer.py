import re


MAX_EMAIL_LENGTH = 20000

URGENCY_PHRASES = (
    "act immediately",
    "urgent action required",
    "account will be suspended",
    "verify your account",
    "immediate action required",
)

CREDENTIAL_PHRASES = (
    "enter your password",
    "confirm your password",
    "share your password",
    "verify your credentials",
)

FINANCIAL_PHRASES = (
    "wire transfer",
    "send gift cards",
    "payment details",
    "bank account details",
)


def analyze_email(raw_email):
    """
    Analyze supplied email text using transparent heuristic rules.
    Does not send, open, or store the email.
    """

    if not isinstance(raw_email, str):
        raise ValueError("Email content must be provided as text.")

    email_text = raw_email.strip()

    if not email_text:
        raise ValueError("Please enter email content.")

    if len(email_text) > MAX_EMAIL_LENGTH:
        raise ValueError("Email content exceeds the maximum length.")

    normalized = email_text.lower()
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

    if any(phrase in normalized for phrase in URGENCY_PHRASES):
        add_indicator(
            "urgency_language",
            20,
            "The message uses language that pressures the recipient to act.",
        )

    if any(phrase in normalized for phrase in CREDENTIAL_PHRASES):
        add_indicator(
            "credential_request",
            30,
            "The message contains language requesting password or credential information.",
        )

    if any(phrase in normalized for phrase in FINANCIAL_PHRASES):
        add_indicator(
            "financial_request",
            25,
            "The message mentions a potentially sensitive financial action.",
        )

    # Look for URLs written directly in the email text.
    urls = re.findall(
        r"https?://[^\s<>\"']+",
        email_text,
        flags=re.IGNORECASE,
    )

    if urls:
        add_indicator(
            "contains_url",
            10,
            "The message contains one or more web links. "
            "Their presence alone does not prove phishing.",
        )

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
            "Potential phishing indicators were found. Review the findings."
            if indicators
            else "No configured email indicators were detected."
        ),
    }
