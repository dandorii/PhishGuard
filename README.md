# 🛡️ PhishGuard — Phishing URL & Email Analyzer

**PhishGuard** is a cybersecurity web application that analyzes URLs and email content for common phishing indicators. Built with Python and Flask, it uses transparent, rule-based heuristics to assign risk scores, classify suspicious content by severity, and help users understand potential phishing threats.

The project focuses on practical cybersecurity learning, secure web application development, transparent detection logic, and responsible handling of user-submitted data.

🌐 **Live Demo:** [https://phishguard-ujkh.onrender.com](https://phishguard-ujkh.onrender.com)  
🔐 **Login:** [Sign in to PhishGuard](https://phishguard-ujkh.onrender.com/login)  
📝 **Register:** [Create an account](https://phishguard-ujkh.onrender.com/register)  
💻 **GitHub Repository:** [dandorii/PhishGuard](https://github.com/dandorii/PhishGuard)

> **Disclaimer:** PhishGuard is an educational cybersecurity project. Its findings are heuristic assessments, not definitive proof that a URL or email is safe or malicious. Always verify suspicious communications through trusted channels.

## ✨ Features

- **URL Analysis** — Evaluates submitted URLs for suspicious characteristics, including IP-based hosts, unusual hostname patterns, non-ASCII characters, and insecure HTTP connections.
- **Email Analysis** — Examines submitted email content for urgency, credential requests, financial requests, and embedded URLs.
- **Risk Scoring** — Assigns a score from 0 to 100 and classifies results as Low, Medium, High, or Critical.
- **Interactive Dashboard** — Displays analysis statistics and recent activity.
- **Private Analysis History** — Allows authenticated users to review and manage their own saved analysis records.
- **User Authentication** — Provides registration, login, session management, and logout functionality.
- **Authentication UI** — Includes responsive sign-in and registration pages, password visibility controls, and password-confirmation feedback.
- **Methodology Page** — Documents the detection rules and explains how risk scores are interpreted.
- **REST API** — Provides endpoints for analysis, application health, dashboard statistics, and analysis history.
- **Database Integration** — Supports local development and PostgreSQL configuration for hosted use.
- **Automated Testing** — Uses pytest to test application behavior, analyzers, authentication, and other components.
- **Responsive Interface** — Uses HTML5, CSS3, and vanilla JavaScript.

## 🧰 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic and detection rules |
| Flask | Web framework and API routes |
| Flask-WTF | CSRF protection for supported forms |
| Argon2id | Password hashing |
| SQLite | Local development database |
| PostgreSQL | Configurable production database |
| HTML5 | Web page structure |
| CSS3 | Styling and responsive layouts |
| JavaScript | Frontend interactions and API requests |
| pytest | Automated testing |
| Gunicorn | Production WSGI server |
| Render | Web application hosting |
| Git and GitHub | Version control and source code hosting |

## 🔐 Authentication and Account Access

PhishGuard requires authentication to access protected features, including private analysis history.

### Getting started

1. **New users:** Visit [`/register`](https://phishguard-ujkh.onrender.com/register) to create an account.
2. **Existing users:** Visit [`/login`](https://phishguard-ujkh.onrender.com/login) to sign in.
3. **Analyze content:** After signing in, navigate to the dashboard and use the available analysis tools.
4. **Review history:** Access your saved analysis records through the history page.
5. **Log out:** Use the application's logout functionality when finished. Logout uses a POST request rather than a direct browser-navigation link.

### Authentication routes

| Route | Purpose |
|---|---|
| `/login` | Sign in to an existing account |
| `/register` | Create an account |
| `/logout` | End the authenticated session |

The application uses server-side validation, password hashing, session handling, and CSRF protection for supported state-changing operations.

**Account security:** Never share your password or submit sensitive personal information to an application unless you understand how that information is handled.

## 📊 Risk Classification

PhishGuard classifies analysis results using the following score ranges:

| Risk Score | Severity |
|---|---|
| 0–29 | Low |
| 30–59 | Medium |
| 60–79 | High |
| 80–100 | Critical |

Scores represent the indicators detected by the configured rules. They are not probabilities that a URL or email is malicious.

A low score does not guarantee that content is legitimate, while a high score does not independently prove malicious intent.

## 🔍 Analysis Methodology

### URL Analyzer

The URL analyzer examines submitted URLs for characteristics such as:

- Use of HTTP instead of HTTPS
- IP addresses used as hostnames
- The presence of `@` in the URL authority
- Unusually long hostnames
- Excessive subdomains or hostname labels
- Non-ASCII hostname characters
- Punycode hostname patterns
- Invalid, incomplete, or excessively long input

Applicable rules contribute to the overall risk score according to their configured weights.

### Email Analyzer

The email analyzer looks for common phishing-related language and patterns, including:

- Urgent or time-sensitive requests
- Requests for account credentials
- Financial requests
- URLs embedded in submitted email content

These checks use rule-based heuristics. They do not inherently establish the sender's identity, verify a website's reputation, or prove that a message is malicious.

### Detection limitations

Phishing techniques change frequently. Attackers can evade simple detection rules, and legitimate messages can trigger suspicious indicators.

PhishGuard should therefore be treated as a learning and preliminary analysis tool rather than a replacement for professional threat intelligence, endpoint protection, or security investigation.

## 🖥️ Application Pages

| Page | Description |
|---|---|
| Login | Authenticate an existing user |
| Registration | Create a new account |
| Dashboard | Review analysis statistics and recent activity |
| URL Analyzer | Analyze a submitted URL |
| Email Analyzer | Examine email content for phishing indicators |
| Analysis History | Review and manage the current user's saved records |
| Methodology | Understand the detection rules and scoring system |

Access to protected pages depends on the user's authentication status.

## 🔌 API Endpoints

The application provides API functionality for health checks, analysis, dashboard statistics, and history management.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/health` | Check application health |
| `GET` | `/api/dashboard-stats` | Retrieve dashboard statistics |
| `POST` | `/api/analyze/url` | Analyze a submitted URL |
| `POST` | `/api/analyze/email` | Analyze submitted email content |
| `GET` | `/api/history` | Retrieve analysis history subject to authentication and ownership checks |
| `DELETE` | `/api/history/<id>` | Delete an analysis record subject to authorization checks |

Request fields, response structures, and authentication requirements are defined by the current application implementation. Refer to `app.py` and the related modules before integrating these endpoints into another application.

**API security:** Protected history operations must enforce authentication and record ownership on the server. Frontend controls alone are not sufficient to enforce authorization.

## 🗂️ Project Structure

The following is a representative overview of the project's main files and directories.

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
│   ├── login.html
│   ├── register.html
│   ├── url_analyzer.html
│   ├── email_analyzer.html
│   ├── history.html
│   └── methodology.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── app.js
│       └── auth.js
└── tests/
    └── ...
```

The exact directory contents may change as the project develops. Consult the repository for the latest files and test modules.

## ⚙️ Installation and Local Setup

### Prerequisites

- Python 3.10 or later
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

If PowerShell blocks activation, you can use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file if your development setup uses environment variables. Do not commit secrets or database credentials to GitHub.

For local development, use the database configuration supported by your current application. If you enable PostgreSQL locally, configure a valid database connection string and the corresponding application settings.

Example variable names used by the deployment configuration:

```dotenv
APP_ENV=development
SECRET_KEY=replace-with-a-strong-random-secret
DATABASE_URL=your-database-connection-string
PHISHGUARD_USE_POSTGRES=1
```

These values are examples, not production credentials. Configure only the variables needed for your selected database mode. Use a strong, private `SECRET_KEY` and keep real credentials out of source control.

### 5. Initialize the database

Follow the database initialization procedure implemented by the project. Ensure that the required tables and schema exist before using registration, authentication, or analysis history.

### 6. Run the application

```bash
python app.py
```

Open the local address shown in the terminal, usually:

```text
http://127.0.0.1:5000
```

Use `/register` to create a local account and `/login` to sign in.

Keep Flask debug mode disabled when running in production.

## 🧪 Running Tests

Run the automated tests from the project root:

```bash
python -m pytest -q
```

To run the authentication UI tests specifically:

```bash
python -m pytest tests/test_auth_ui.py -q
```

The authentication UI tests most recently passed **19 tests** during the redesign work.

Test results can change as the codebase evolves. Run the test suite against the exact commit you intend to deploy and investigate any failures before release.

## 🔒 Security Considerations

PhishGuard incorporates several security-oriented design practices:

- **No automatic URL fetching:** Submitted URLs are analyzed as input rather than automatically visited by the application.
- **Password hashing:** User passwords are hashed with Argon2id rather than stored as plaintext.
- **CSRF protection:** Supported forms and state-changing operations use CSRF protections.
- **Private analysis history:** History access is restricted by authentication and user ownership.
- **Metadata-focused storage:** The application is designed to avoid retaining original submitted URLs or full email bodies in analysis history by default.
- **Parameterized database operations:** Database queries should use parameterized statements to reduce SQL injection risks.
- **Safe frontend rendering:** User-controlled content should be rendered as text rather than interpreted as HTML.
- **Input validation:** Submitted URLs, email content, and other user inputs are subject to application validation.
- **Secret management:** Private configuration values should be stored in environment variables and excluded from source control.

These measures do not constitute a complete security audit. Review the current implementation and configuration before using the application with sensitive data or relying on it in a production environment.

## 🚀 Deployment

PhishGuard is hosted on [Render](https://render.com/).

**Live application:** [https://phishguard-ujkh.onrender.com](https://phishguard-ujkh.onrender.com)

The production service is configured to deploy from the `feature/responsive-navigation` branch. Check the Render service configuration before changing branches or deployment settings.

### Typical Render configuration

**Build command**

```bash
pip install -r requirements.txt
```

**Start command**

```bash
gunicorn app:app
```

The repository's `Procfile` should match the intended production start command.

### Production environment

Configure required environment variables in Render's environment settings. These may include:

- `APP_ENV`
- `SECRET_KEY`
- `DATABASE_URL`
- `PHISHGUARD_USE_POSTGRES`

Use the exact settings required by the current application. Never place production secrets in the README or commit them to the repository.

### Database persistence

The application supports SQLite for local development and PostgreSQL configuration for hosted use.

A SQLite database stored on an ephemeral hosting filesystem may be lost after a restart, redeployment, or instance replacement. For persistent hosted analysis history, use the configured PostgreSQL database or another properly backed-up persistent storage solution.

### Deployment considerations

Render's free services may spin down after periods of inactivity, which can cause a delay on the first request. Check the service's current plan and hosting configuration for availability limitations.

## 🎯 Project Objectives

PhishGuard was developed to explore practical cybersecurity and software development concepts:

- Identifying common phishing indicators
- Designing transparent risk-scoring rules
- Building a Flask web application and REST API
- Integrating a relational database
- Implementing authentication and access controls
- Protecting user-specific analysis history
- Developing a responsive frontend
- Writing automated tests
- Applying secure input handling and output rendering
- Deploying a Python web application to a public hosting platform

## 🔮 Potential Future Improvements

Possible future enhancements include:

- Integration with trusted URL reputation services
- More advanced email header and sender analysis
- Improved detection rules and false-positive handling
- Additional API validation and authorization tests
- Expanded security testing and vulnerability assessment
- Exportable analysis reports
- Improved monitoring and error reporting
- Further accessibility and responsive-design improvements
- Additional documentation for API consumers

These are potential enhancements rather than claims about features already implemented.

## 👨‍💻 Author

Developed as a personal cybersecurity learning and portfolio project by a BS Cybersecurity student at Holy Angel University.

**Focus Areas:** Cybersecurity, Python Development, Web Application Security, and Threat Analysis.

## 📄 License

No license has been specified in this README. Unless a license is added to the repository, others do not automatically receive permission to reuse, modify, or redistribute the code.

Consider adding an appropriate license if you intend to make the project openly reusable.
