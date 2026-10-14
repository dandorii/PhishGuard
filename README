# 🛡️ PhishGuard — Phishing URL & Email Analyzer

**PhishGuard** is a beginner-friendly cybersecurity web application designed to analyze URLs and email content for common phishing indicators. It uses transparent, rule-based heuristics to assign risk scores, categorize results by severity, and help users understand potentially suspicious content.

🌐 **Live Demo:** https://phishguard-ujkh.onrender.com  
💻 **GitHub Repository:** https://github.com/dandorii/PhishGuard

> **Disclaimer:** PhishGuard is an educational cybersecurity project. Its results are heuristic assessments, not definitive proof that a URL or email is safe or malicious.

## ✨ Features

- **URL Analysis** — Examines submitted URLs for suspicious characteristics, including IP-based hosts, unusual hostname patterns, non-ASCII characters, and insecure HTTP connections.
- **Email Analysis** — Checks email content for urgency, credential requests, financial requests, and URLs commonly associated with phishing attempts.
- **Risk Scoring** — Assigns a score from 0 to 100 and categorizes results as Low, Medium, High, or Critical.
- **Dashboard** — Displays total scans, suspicious results, high-risk results, and recent analysis activity.
- **Scan History** — Records analysis metadata and provides a history interface for reviewing previous scans.
- **Methodology Page** — Explains the rules used to evaluate URLs and email content.
- **REST API** — Provides endpoints for analysis, dashboard statistics, application health, and scan history.
- **Automated Testing** — Includes tests for routes, analyzers, database operations, history API behavior, and methodology.
- **Responsive Web Interface** — Built with HTML, CSS, and vanilla JavaScript.

## 🧰 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Flask | Web framework and API routes |
| SQLite | Local database for scan metadata |
| HTML5 | Web page structure |
| CSS3 | Styling and responsive layout |
| JavaScript | Interactive interface and API requests |
| pytest | Automated testing |
| Gunicorn | Production WSGI server |
| Render | Web application hosting |
| Git and GitHub | Version control and source code hosting |

## 📊 Risk Classification

PhishGuard uses a rule-based scoring system with the following severity levels:

| Risk Score | Severity |
|---|---|
| 0–29 | Low |
| 30–59 | Medium |
| 60–79 | High |
| 80–100 | Critical |

The score represents the indicators detected by the analyzer. A low score does not guarantee that the submitted content is legitimate, and a high score does not independently prove malicious intent.

## 🔍 Analysis Methodology

### URL Analyzer

The URL analyzer checks submitted URLs for characteristics such as:

- Use of HTTP instead of HTTPS
- IP addresses used as hostnames
- The presence of `@` in the URL authority
- Unusually long hostnames
- Hostnames with many subdomains or labels
- Non-ASCII hostname characters
- Punycode hostname patterns
- Invalid, incomplete, or excessively long input

Each applicable rule contributes to the risk score according to its configured weight.

### Email Analyzer

The email analyzer looks for common phishing-related language and patterns, including:

- Urgent or time-sensitive requests
- Requests for credentials
- Financial requests
- URLs contained in the submitted email content

These checks are transparent heuristics. They do not use machine learning, reputation databases, or a guarantee of malicious intent.

## 🖥️ Application Pages

| Page | Description |
|---|---|
| Dashboard | Overview of scan statistics and recent activity |
| URL Analyzer | Analyze a submitted URL |
| Email Analyzer | Examine email content for phishing indicators |
| History | Review saved analysis records |
| Methodology | Learn how the detection rules and scoring work |

## 🔌 API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/health` | Check application health |
| `GET` | `/api/dashboard-stats` | Retrieve dashboard statistics |
| `POST` | `/api/analyze/url` | Analyze a URL |
| `POST` | `/api/analyze/email` | Analyze email content |
| `GET` | `/api/history` | Retrieve scan history |
| `DELETE` | `/api/history/<id>` | Delete a history record |

The analysis endpoints accept submitted data according to the application's request format. Consult `app.py` for the exact request fields and response structure.

## 🗂️ Project Structure

```text
PhishGuard/
├── app.py
├── requirements.txt
├── Procfile
├── .gitignore
├── analyzers/
│   ├── url_analyzer.py
│   └── email_analyzer.py
├── database/
│   ├── __init__.py
│   └── db.py
├── templates/
│   ├── index.html
│   ├── url_analyzer.html
│   ├── email_analyzer.html
│   ├── history.html
│   └── methodology.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── tests/
    ├── test_routes.py
    ├── test_url_analyzer.py
    ├── test_email_analyzer.py
    ├── test_database.py
    ├── test_history_api.py
    └── test_methodology.py
```

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.10 or later recommended
- Git
- A code editor, such as Visual Studio Code

### 1. Clone the repository

```bash
git clone https://github.com/dandorii/PhishGuard.git
cd PhishGuard
```

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

Open the local address shown in the terminal, usually:

```text
http://127.0.0.1:5000
```

Keep the development server's debug mode disabled when deploying to production.

## 🧪 Running Tests

Run the automated test suite from the project root:

```bash
python -m pytest -q
```

The project's test suite previously passed **48 tests** during development. Run the command above against your current checkout to verify its present status.

## 🔐 Security Considerations

PhishGuard incorporates several basic security practices:

- **No automatic URL fetching:** Submitted URLs are analyzed as input rather than opened or visited by the application.
- **Metadata-focused storage:** Scan history stores analysis results and metadata rather than the original submitted URL or full email body.
- **Parameterized SQL queries:** Database operations should use parameterized queries to reduce SQL injection risks.
- **Safe frontend rendering:** User-controlled content should be inserted using `textContent` rather than interpreted as HTML.
- **Input validation:** URL and email input lengths are restricted, and malformed inputs are checked.
- **Heuristic limitations:** Attackers can evade simple rules, and legitimate content can trigger suspicious indicators.

These safeguards do not constitute a complete security audit. Additional testing is necessary before using the application with sensitive information or in a production environment.

## 🚀 Deployment

PhishGuard is deployed using [Render](https://render.com/).

The repository's `Procfile` specifies:

```text
web: gunicorn app:app
```

Typical Render configuration:

**Build command**
```bash
pip install -r requirements.txt
```

**Start command**
```bash
gunicorn app:app
```

**Deployment branch:** `main`

### Database persistence note

The current implementation uses SQLite. On a free hosting service with an ephemeral filesystem, database records may disappear after a restart, redeployment, or instance replacement. For persistent hosted history, consider a managed PostgreSQL database or an appropriately configured persistent disk.

## 🎯 Project Objectives

This project was developed to explore and demonstrate foundational cybersecurity and software development concepts:

- Identifying common phishing indicators
- Designing transparent risk-scoring rules
- Developing a Flask web application and REST API
- Integrating a relational database
- Building an interactive dashboard
- Writing automated tests
- Applying secure input handling and frontend rendering practices
- Deploying a Python application to a public hosting platform

## 🔮 Potential Future Improvements

- Integration with trusted URL reputation services
- More advanced email header and sender analysis
- Improved detection rules and false-positive handling
- Additional API and input validation tests
- Persistent PostgreSQL storage
- Exportable scan reports
- Authentication and access controls
- Expanded documentation and security testing

## 👨‍💻 Author

Developed as a personal cybersecurity learning and portfolio project by a BS Cybersecurity student at Holy Angel University.

**Focus Areas:** Cybersecurity, Python Development, Web Application Security, and Threat Analysis.

## 📄 License

No license has been specified yet. Unless a license is added to this repository, the code is not automatically granted an open-source license for reuse or redistribution.
