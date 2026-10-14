from analyzers.url_analyzer import analyze_url
from analyzers.email_analyzer import analyze_email
from flask import Flask, jsonify, render_template, request
from database.db import (
    init_db,
    save_analysis,
    get_recent_analyses,
    delete_analysis,
    get_dashboard_stats,
)

app = Flask(__name__)


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

    try:
        result = analyze_url(url)
    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    save_analysis("url", result)
    return jsonify(result)



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

    try:
        result = analyze_email(email_text)
    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    save_analysis("email", result)
    return jsonify(result)


@app.get("/email-analyzer")
def email_analyzer_page():
    return render_template("email_analyzer.html")


@app.get("/history")
def history_page():
    return render_template("history.html")


@app.get("/api/history")
def history_api():
    history = get_recent_analyses()
    return jsonify(history)


@app.get("/api/dashboard-stats")
def api_dashboard_stats():
    return jsonify(get_dashboard_stats())


@app.delete("/api/history/<int:analysis_id>")
def delete_history_api(analysis_id):
    deleted = delete_analysis(analysis_id)

    if not deleted:
        return jsonify({
            "error": "Analysis record not found."
        }), 404

    return jsonify({
        "message": "Analysis record deleted successfully."
    })


@app.get("/methodology")
def methodology_page():
    return render_template("methodology.html")

init_db()


if __name__ == "__main__":
    app.run(debug=True)

