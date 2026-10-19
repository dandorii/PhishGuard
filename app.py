from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

from analyzers.url_analyzer import analyze_url
from analyzers.email_analyzer import analyze_email
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    flash,
    redirect,
    session,
    url_for,
    abort,
    g,
)
from urllib.parse import urlsplit, urljoin
from database.db import (
    init_db,
    save_analysis,
    get_recent_analyses,
    delete_analysis,
    get_dashboard_stats,
    create_user,
    get_user_by_email,
    get_user_by_id,
    verify_password,
)

import os

app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("APP_ENV") == "production",
    PERMANENT_SESSION_LIFETIME=1800,
)

csrf = CSRFProtect(app)  # Enable CSRF protection

def get_current_user():
    """Return the authenticated user, or None if the session is invalid."""
    user_id = session.get("user_id")

    if type(user_id) is not int or user_id < 1:
        return None

    user = get_user_by_id(user_id)

    if user is None:
        session.clear()
        return None

    return user

def is_safe_redirect_target(target):
    """Allow redirects only to local URLs on this application."""
    if not target:
        return False

    host_url = urlsplit(request.host_url)
    redirect_url = urlsplit(urljoin(request.host_url, target))

    return (
        redirect_url.scheme in {"http", "https"}
        and redirect_url.netloc == host_url.netloc
        and redirect_url.scheme == host_url.scheme
    )

@app.get("/")
def home():
    return render_template("index.html")


@app.get("/url-analyzer")
def url_analyzer():
    return render_template("url_analyzer.html")


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "application": "PhishGuard"
    })

@csrf.exempt
@app.post("/api/analyze/url")
def analyze_url_route():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Send a valid JSON object."
        }), 400

    url = data.get("url")

    if not isinstance(url, str):
        return jsonify({
            "error": "The URL must be provided as text."
        }), 400

    if len(url) > 2048:
        return jsonify({
            "error": "The URL must not exceed 2048 characters."
        }), 400

    try:
        result = analyze_url(url)
    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    user_id = session.get("user_id")

    if user_id is not None:
        save_analysis("url", result, user_id=user_id)

    return jsonify(result)


@csrf.exempt
@app.post("/api/analyze/email")
def analyze_email_route():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Send a valid JSON object."
        }), 400

    email_text = data.get("email")

    if not isinstance(email_text, str):
        return jsonify({
            "error": "Email content must be provided as text."
        }), 400

    if len(email_text) > 50000:
        return jsonify({
            "error": "Email content must not exceed 50000 characters."
        }), 400

    try:
        result = analyze_email(email_text)
    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    user_id = session.get("user_id")

    if user_id is not None:
        save_analysis("email", result, user_id=user_id)

    return jsonify(result)


@app.get("/email-analyzer")
def email_analyzer_page():
    return render_template("email_analyzer.html")


@app.get("/history")
def history_page():
    if get_current_user() is None:
        return redirect(url_for("login", next=request.path))

    return render_template("history.html")


@app.get("/api/history")
def history_api():
    user = get_current_user()

    if user is None:
        return jsonify({"error": "Authentication required."}), 401

    return jsonify(get_recent_analyses(user["id"]))


@app.get("/api/dashboard-stats")
def dashboard_stats_api():
    user = get_current_user()

    if user is None:
        return jsonify({"error": "Authentication required."}), 401

    return jsonify(get_dashboard_stats(user["id"]))


@app.delete("/api/history/<int:analysis_id>")
def delete_history_api(analysis_id):
    user = get_current_user()

    if user is None:
        return jsonify({"error": "Authentication required."}), 401

    deleted = delete_analysis(analysis_id, user["id"])

    if not deleted:
        return jsonify({"error": "Analysis not found."}), 404

    return jsonify({"message": "Analysis deleted successfully."})


@app.get("/methodology")
def methodology_page():
    return render_template("methodology.html")

init_db()


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if password != confirm_password:
            flash("The passwords do not match.")
            return render_template("register.html"), 400

        try:
            user_id = create_user(email, password)
        except ValueError as error:
            flash(str(error))
            return render_template("register.html"), 400

        # Start a fresh session after successful registration.
        session.clear()
        session["user_id"] = user_id
        session.permanent = True

        flash("Your account was created successfully.")
        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        try:
            user = get_user_by_email(email)
        except ValueError:
            user = None

        if not verify_password(user, password):
            flash("Invalid email or password.")
            return render_template("login.html"), 401

        # Clear any previous session state before signing in.
        session.clear()
        session["user_id"] = user["id"]
        session.permanent = True

        flash("You are now signed in.")

        next_url = request.form.get("next") or request.args.get("next")

        if is_safe_redirect_target(next_url):
            return redirect(next_url)

        return redirect(url_for("home"))

    return render_template("login.html")


@app.post("/logout")
def logout():
    session.clear()
    flash("You have been signed out.")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=False)

