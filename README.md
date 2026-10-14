# PhishGuard — Phishing URL & Email Analyzer

PhishGuard is an educational cybersecurity project. It inspects URLs and email
text for common phishing indicators using transparent, rule-based heuristics.

**Live site:** https://phishguard-ujkh.onrender.com/

PhishGuard never opens, visits, or fetches submitted URLs. It stores only
analysis metadata (scores, severity, and rule identifiers), never the submitted
URL or email body.

> PhishGuard's scores are heuristic indicators, not proof that content is
> malicious or safe.

## Features

- Dashboard with live scan statistics and recent activity
- URL analyzer with explainable indicators
- Email analyzer with explainable indicators
- Analysis history with per-record deletion (confirmed in-page)
- Detection methodology page documenting every rule and its points
- Light and dark themes, following the operating-system setting until you choose one
- Responsive layout with a mobile menu, keyboard support, and visible focus states

## Technology

- Python, Flask, Jinja templates
- SQLite (metadata only)
- HTML5, CSS3 (design tokens for theming), vanilla JavaScript
- pytest
- Gunicorn (production), deployed on Render

## Run locally

Tested with Python 3.13.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

The SQLite database is created automatically at `instance/phishguard.db`.

## Run the tests

```bash
python -m pytest -q
```

The tests use a temporary database, so they never change your real history.

### Manual checks

The automated tests cover the API, the database, and the page markup. Some
behavior needs a browser. Check it at 320, 375, 768, 1024, and desktop widths:

- The menu opens and closes with the button, Escape, a link click, and an outside click.
- Keyboard users can reach the menu button and links, and focus is always visible.
- The theme toggle switches themes and the choice survives a page refresh.
- Analysis forms, results, and the dashboard still work after switching themes.
- Deleting a history record asks for confirmation first.

## Project layout

```
app.py                 Flask routes and JSON API
analyzers/             Heuristic URL and email rules (scoring)
database/db.py         SQLite access (parameterized queries)
templates/base.html    Shared layout: navigation, theme, status, footer
templates/*.html       Page content for each screen
static/css/style.css   Design tokens (dark and light) and component styles
static/js/app.js       Menu, theme, analysis, history, and dashboard behavior
static/favicon.svg     Shield-and-check browser icon
tests/                 pytest suite
```

## Changing the scoring

Scoring weights and thresholds live in `analyzers/`. Changing them affects
results for every user, so update the Methodology page and the tests together.
