const urlForm = document.getElementById("url-form");

if (urlForm) {
    urlForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const urlInput = document.getElementById("url-input");
        const message = document.getElementById("url-message");
        const submitButton = urlForm.querySelector(
            'button[type="submit"]'
        );

        const url = urlInput.value.trim();

        message.hidden = false;
        message.textContent = "Analyzing URL structure...";
        submitButton.disabled = true;

        try {
            const response = await fetch("/api/analyze/url", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ url })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Analysis failed.");
            }

            displayUrlResults(data, message);
        } catch (error) {
            message.replaceChildren();

            const errorText = document.createElement("p");
            errorText.textContent = error.message;
            message.appendChild(errorText);
        } finally {
            submitButton.disabled = false;
        }
    });
}

function displayUrlResults(data, container) {
    container.replaceChildren();

    const heading = document.createElement("h2");
    heading.textContent = "Analysis Results";

    const score = document.createElement("p");
    score.textContent = `Heuristic Risk Score: ${data.score}/100`;

    const severity = document.createElement("p");
    severity.textContent = `Severity: ${data.severity}`;

    const explanation = document.createElement("p");
    explanation.textContent = data.message;

    container.append(heading, score, severity, explanation);

    const listHeading = document.createElement("h3");
    listHeading.textContent = "Detected Indicators";
    container.appendChild(listHeading);

    if (data.indicators.length === 0) {
        const item = document.createElement("p");
        item.textContent = "No configured indicators detected.";
        container.appendChild(item);
    } else {
        const list = document.createElement("ul");

        for (const indicator of data.indicators) {
            const item = document.createElement("li");
            item.textContent =
                `${indicator.explanation} (+${indicator.points} points)`;
            list.appendChild(item);
        }

        container.appendChild(list);
    }

    const disclaimer = document.createElement("p");
    disclaimer.textContent =
        "This heuristic score is not a probability. " +
        "A low score does not guarantee that a URL is safe.";

    container.appendChild(disclaimer);
}


const emailForm = document.getElementById("email-form");

if (emailForm) {
    emailForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const emailInput = document.getElementById("email-input");
        const message = document.getElementById("email-message");
        const submitButton = emailForm.querySelector(
            'button[type="submit"]'
        );

        message.hidden = false;
        message.textContent = "Analyzing email text...";
        submitButton.disabled = true;

        try {
            const response = await fetch("/api/analyze/email", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: emailInput.value
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Email analysis failed.");
            }

            displayUrlResults(data, message);
        } catch (error) {
            message.replaceChildren();

            const errorText = document.createElement("p");
            errorText.textContent = error.message;
            message.appendChild(errorText);
        } finally {
            submitButton.disabled = false;
        }
    });
}


const historyBody = document.getElementById("history-table-body");
const historyStatus = document.getElementById("history-status");
const refreshHistoryButton = document.getElementById("refresh-history");

if (historyBody && historyStatus) {
    async function loadHistory() {
        historyStatus.textContent = "Loading analysis history...";
        historyBody.replaceChildren();

        try {
            const response = await fetch("/api/history");
            const history = await response.json();

            if (!response.ok) {
                throw new Error("Unable to load analysis history.");
            }

            if (history.length === 0) {
                historyStatus.textContent = "No analyses recorded yet.";
                return;
            }

            historyStatus.textContent =
                `${history.length} recent analysis record(s).`;

            history.forEach((record) => {
                const row = document.createElement("tr");

                const values = [
                    record.id,
                    record.analysis_type.toUpperCase(),
                    new Date(record.analyzed_at).toLocaleString(),
                    `${record.score}/100`,
                    record.severity,
                    record.indicator_count
                ];

                values.forEach((value) => {
                    const cell = document.createElement("td");
                    cell.textContent = String(value);
                    row.appendChild(cell);
                });

                
                    const actionCell = document.createElement("td");
                    const deleteButton = document.createElement("button");

                    deleteButton.type = "button";
                    deleteButton.className = "delete-history-button";
                    deleteButton.setAttribute(
                        "aria-label",
                        `Delete analysis record ${record.id}`
                    );

                    // Create the trash icon safely using SVG elements.
                    const trashIcon = document.createElementNS(
                        "http://www.w3.org/2000/svg",
                        "svg"
                    );

                    trashIcon.setAttribute("width", "15");
                    trashIcon.setAttribute("height", "15");
                    trashIcon.setAttribute("viewBox", "0 0 24 24");
                    trashIcon.setAttribute("fill", "none");
                    trashIcon.setAttribute("stroke", "currentColor");
                    trashIcon.setAttribute("stroke-width", "2");
                    trashIcon.setAttribute("stroke-linecap", "round");
                    trashIcon.setAttribute("stroke-linejoin", "round");
                    trashIcon.setAttribute("aria-hidden", "true");
                    trashIcon.classList.add("button-icon");

                    const trashPath = document.createElementNS(
                        "http://www.w3.org/2000/svg",
                        "path"
                    );
                    trashPath.setAttribute("d", "M3 6h18");
                    trashIcon.appendChild(trashPath);

                    const trashBody = document.createElementNS(
                        "http://www.w3.org/2000/svg",
                        "path"
                    );
                    trashBody.setAttribute(
                        "d",
                        "M8 6V4h8v2m-11 0 1 14h12l1-14M10 11v5m4-5v5"
                    );
                    trashIcon.appendChild(trashBody);

                    const deleteLabel = document.createElement("span");
                    deleteLabel.textContent = "Delete";

                    deleteButton.append(trashIcon, deleteLabel);


                deleteButton.addEventListener("click", async () => {
                    const confirmed = window.confirm(
                        "Delete this analysis record?"
                    );

                    if (!confirmed) return;

                    deleteButton.disabled = true;

                    try {
                        const deleteResponse = await fetch(
                            `/api/history/${record.id}`,
                            { method: "DELETE" }
                        );

                        if (!deleteResponse.ok) {
                            throw new Error("Unable to delete record.");
                        }

                        await loadHistory();
                    } catch {
                        historyStatus.textContent =
                            "Could not delete the record. Please try again.";
                        deleteButton.disabled = false;
                    }
                });

                actionCell.appendChild(deleteButton);
                row.appendChild(actionCell);
                historyBody.appendChild(row);
            });
        } catch {
            historyStatus.textContent =
                "Could not load history. Please refresh and try again.";
        }
    }

    refreshHistoryButton?.addEventListener("click", loadHistory);
    loadHistory();
}

async function loadDashboard() {
    const totalScans = document.getElementById("total-scans");
    const suspiciousResults = document.getElementById("suspicious-results");
    const highRiskResults = document.getElementById("high-risk-results");
    const activityBody = document.getElementById("recent-activity-body");
    const dashboardStatus = document.getElementById("dashboard-status");

    // Do nothing on pages that don't contain the dashboard.
    if (
        !totalScans ||
        !suspiciousResults ||
        !highRiskResults ||
        !activityBody ||
        !dashboardStatus
    ) {
        return;
    }

    try {
        const response = await fetch("/api/dashboard-stats");

        if (!response.ok) {
            throw new Error("Could not load dashboard data.");
        }

        const data = await response.json();

        totalScans.textContent = data.total_scans;
        suspiciousResults.textContent = data.suspicious_results;
        highRiskResults.textContent = data.high_risk_results;

        activityBody.replaceChildren();

        if (!data.recent_activity || data.recent_activity.length === 0) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");

            cell.colSpan = 6;
            cell.textContent = "No analyses recorded yet.";

            row.appendChild(cell);
            activityBody.appendChild(row);
        } else {
            data.recent_activity.forEach((record) => {
                const row = document.createElement("tr");

                const idCell = document.createElement("td");
                idCell.textContent = record.id;
                row.appendChild(idCell);

                const typeCell = document.createElement("td");
                typeCell.textContent =
                    record.analysis_type === "url" ? "URL" : "Email";
                row.appendChild(typeCell);

                const dateCell = document.createElement("td");
                const date = new Date(record.analyzed_at);

                dateCell.textContent = Number.isNaN(date.getTime())
                    ? "Unknown date"
                    : date.toLocaleString();
                row.appendChild(dateCell);

                const resultCell = document.createElement("td");
                const riskBadge = document.createElement("span");

                const severity = String(record.severity || "Low").toLowerCase();
                const allowedSeverities = ["low", "medium", "high", "critical"];
                const safeSeverity = allowedSeverities.includes(severity)
                    ? severity
                    : "low";

                riskBadge.className = `risk ${safeSeverity}`;
                riskBadge.textContent =
                    safeSeverity.charAt(0).toUpperCase() +
                    safeSeverity.slice(1);

                resultCell.appendChild(riskBadge);
                row.appendChild(resultCell);

                const scoreCell = document.createElement("td");
                scoreCell.textContent = `${record.score}/100`;
                row.appendChild(scoreCell);

                const indicatorsCell = document.createElement("td");
                indicatorsCell.textContent = record.indicator_count;
                row.appendChild(indicatorsCell);

                activityBody.appendChild(row);
            });
        }

        dashboardStatus.textContent = "Data updated";
    } catch (error) {
        totalScans.textContent = "—";
        suspiciousResults.textContent = "—";
        highRiskResults.textContent = "—";

        activityBody.replaceChildren();

        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 6;
        cell.textContent =
            "Unable to load dashboard data. Check that Flask is running and the dashboard API is available.";

        row.appendChild(cell);
        activityBody.appendChild(row);

        dashboardStatus.textContent = "Unavailable";
        console.error("Dashboard loading error:", error);
    }
}

loadDashboard();

