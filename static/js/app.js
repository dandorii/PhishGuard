// Mobile navigation: open/close the menu, keep aria-expanded in sync,
// and close it with Escape, after a link is chosen, or on outside click.
(function setupMobileNavigation() {
    const sidebar = document.getElementById("site-sidebar");
    const toggle = document.getElementById("nav-toggle");

    if (!sidebar || !toggle) return;

    const mobileQuery = window.matchMedia("(max-width: 650px)");

    function setMenuOpen(isOpen) {
        sidebar.classList.toggle("is-open", isOpen);
        toggle.setAttribute("aria-expanded", String(isOpen));
    }

    function isMenuOpen() {
        return sidebar.classList.contains("is-open");
    }

    toggle.addEventListener("click", () => {
        setMenuOpen(!isMenuOpen());
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && isMenuOpen()) {
            setMenuOpen(false);
            toggle.focus();
        }
    });

    sidebar.querySelectorAll(".nav-link").forEach((link) => {
        link.addEventListener("click", () => setMenuOpen(false));
    });

    document.addEventListener("click", (event) => {
        if (isMenuOpen() && !sidebar.contains(event.target)) {
            setMenuOpen(false);
        }
    });

    // When the layout becomes wide, the sidebar is always visible,
    // so reset the mobile state to keep aria-expanded accurate.
    mobileQuery.addEventListener("change", (event) => {
        if (!event.matches) {
            setMenuOpen(false);
        }
    });
})();

// Theme toggle: an explicit choice is saved and restored on later visits.
// Without a saved choice, the page follows the operating-system preference.
(function setupThemeToggle() {
    const STORAGE_KEY = "phishguard-theme";
    const root = document.documentElement;
    const button = document.getElementById("theme-toggle");
    const label = button ? button.querySelector(".theme-label") : null;
    const lightQuery = window.matchMedia("(prefers-color-scheme: light)");

    function savedTheme() {
        try {
            const value = localStorage.getItem(STORAGE_KEY);
            return value === "light" || value === "dark" ? value : null;
        } catch {
            return null;
        }
    }

    function saveTheme(theme) {
        try {
            localStorage.setItem(STORAGE_KEY, theme);
        } catch {
            // Storage is unavailable; the choice still applies for this page view.
        }
    }

    function currentTheme() {
        const explicit = root.getAttribute("data-theme");

        if (explicit === "light" || explicit === "dark") {
            return explicit;
        }

        return lightQuery.matches ? "light" : "dark";
    }

    function renderButton() {
        if (!button || !label) return;

        const nextTheme = currentTheme() === "dark" ? "light" : "dark";
        label.textContent = `Switch to ${nextTheme}`;
    }

    if (button) {
        button.addEventListener("click", () => {
            const nextTheme = currentTheme() === "dark" ? "light" : "dark";

            root.setAttribute("data-theme", nextTheme);
            saveTheme(nextTheme);
            renderButton();
        });
    }

    // Follow OS changes only when the user has not chosen a theme.
    lightQuery.addEventListener("change", () => {
        if (savedTheme() === null) {
            root.removeAttribute("data-theme");
            renderButton();
        }
    });

    renderButton();
})();

// ---------------------------------------------------------------------
// Shared helpers
// ---------------------------------------------------------------------

const NETWORK_ERROR_MESSAGE =
    "Could not reach PhishGuard. Check your connection and try again.";
const UNEXPECTED_RESPONSE_MESSAGE =
    "PhishGuard returned an unexpected response. Please try again.";

async function readJson(response) {
    try {
        return await response.json();
    } catch {
        return null;
    }
}

// Sends an analysis request and returns the parsed result.
// Throws an Error whose message is safe to show to the user.
async function postAnalysis(endpoint, body, fallbackMessage) {
    let response;

    try {
        response = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
    } catch {
        throw new Error(NETWORK_ERROR_MESSAGE);
    }

    const data = await readJson(response);

    if (!response.ok) {
        throw new Error(
            data && typeof data.error === "string" ? data.error : fallbackMessage
        );
    }

    if (!data || typeof data.score !== "number") {
        throw new Error(UNEXPECTED_RESPONSE_MESSAGE);
    }

    return data;
}

// ---------------------------------------------------------------------
// System status (replaces the static "SYSTEM ONLINE" label)
// ---------------------------------------------------------------------

(function setupSystemStatus() {
    const statusElement = document.getElementById("system-status");

    if (!statusElement) return;

    async function checkStatus() {
        try {
            const response = await fetch("/api/health", { cache: "no-store" });
            const data = await readJson(response);

            if (response.ok && data && data.status === "ok") {
                statusElement.textContent = "● SYSTEM ONLINE";
                statusElement.classList.remove("is-down");
                return;
            }

            throw new Error("Unhealthy response");
        } catch {
            statusElement.textContent = "● SERVICE UNAVAILABLE";
            statusElement.classList.add("is-down");
        }
    }

    checkStatus();
})();

// ---------------------------------------------------------------------
// Analyzer results
// ---------------------------------------------------------------------

const SEVERITY_LEVELS = ["Low", "Medium", "High", "Critical"];

const RECOMMENDED_STEPS = {
    Low: [
        "Confirm the sender or website through a channel you already trust before acting on it.",
        "Do not enter passwords or payment details unless you are certain of the destination.",
    ],
    Medium: [
        "Do not click links or open attachments until the source is verified.",
        "Contact the organization using contact details you already have, not those in this content.",
    ],
    High: [
        "Avoid clicking links, opening attachments, or entering credentials.",
        "Report the content to your security team or email provider.",
    ],
    Critical: [
        "Do not interact with the content: no links, attachments, or credentials.",
        "Report it to your security team or email provider, then delete it.",
        "If you already entered a password, change it and turn on multi-factor authentication.",
    ],
};

const DISCLAIMER_TEXT =
    "PhishGuard uses heuristic rules. This score is not proof that the content " +
    "is malicious or safe, and a low score does not guarantee that it is safe.";

function addSummaryItem(list, label, value) {
    const item = document.createElement("div");
    const term = document.createElement("dt");
    const description = document.createElement("dd");

    term.textContent = label;

    if (value instanceof Node) {
        description.appendChild(value);
    } else {
        description.textContent = value;
    }

    item.append(term, description);
    list.appendChild(item);
}

function createList(items, ordered = false) {
    const list = document.createElement(ordered ? "ol" : "ul");

    items.forEach((text) => {
        const item = document.createElement("li");
        item.textContent = text;
        list.appendChild(item);
    });

    return list;
}

function displayResults(data, container, kind, onReset) {
    container.replaceChildren();

    const severity = SEVERITY_LEVELS.includes(data.severity)
        ? data.severity
        : "Low";
    const noun = kind === "url" ? "URL" : "email";

    const heading = document.createElement("h2");
    heading.textContent = "Analysis Results";

    const summary = document.createElement("dl");
    summary.className = "result-summary";

    addSummaryItem(summary, "Heuristic risk score", `${data.score}/100`);

    const severityBadge = document.createElement("span");
    severityBadge.className = `risk ${severity.toLowerCase()}`;
    severityBadge.textContent = severity;

    addSummaryItem(summary, "Severity", severityBadge);

    const explanation = document.createElement("p");
    explanation.textContent = data.message;

    container.append(heading, summary, explanation);

    const indicatorsHeading = document.createElement("h3");
    indicatorsHeading.textContent = "Detected indicators";
    container.appendChild(indicatorsHeading);

    if (data.indicators.length === 0) {
        const none = document.createElement("p");
        none.textContent = "No configured indicators were detected.";
        container.appendChild(none);
    } else {
        container.appendChild(
            createList(
                data.indicators.map(
                    (indicator) =>
                        `${indicator.explanation} (+${indicator.points} points)`
                )
            )
        );
    }

    const stepsHeading = document.createElement("h3");
    stepsHeading.textContent = "Recommended next steps";
    container.appendChild(stepsHeading);
    container.appendChild(createList(RECOMMENDED_STEPS[severity], true));

    const disclaimer = document.createElement("p");
    disclaimer.className = "result-disclaimer";
    disclaimer.textContent = DISCLAIMER_TEXT;
    container.appendChild(disclaimer);

    const actions = document.createElement("div");
    actions.className = "result-actions";

    const resetButton = document.createElement("button");
    resetButton.type = "button";
    resetButton.className = "action-button terminal";
    resetButton.textContent = `Analyze another ${noun}`;
    resetButton.addEventListener("click", onReset);

    actions.appendChild(resetButton);
    container.appendChild(actions);
}

function showAnalysisError(container, text) {
    container.replaceChildren();

    const errorText = document.createElement("p");
    errorText.className = "result-error";
    errorText.textContent = text;

    container.appendChild(errorText);
}

async function runAnalysis(options) {
    const {
        endpoint,
        body,
        fallbackMessage,
        kind,
        progressText,
        container,
        input,
        submitButton,
    } = options;

    const idleLabel = submitButton.textContent;

    container.hidden = false;
    container.setAttribute("aria-busy", "true");
    container.textContent = progressText;
    submitButton.disabled = true;
    submitButton.classList.add("is-loading");
    submitButton.textContent = "Analyzing";

    try {
        const data = await postAnalysis(endpoint, body, fallbackMessage);

        displayResults(data, container, kind, () => {
            container.replaceChildren();
            container.hidden = true;
            input.value = "";
            input.focus();
        });
    } catch (error) {
        showAnalysisError(container, error.message);
    } finally {
        container.setAttribute("aria-busy", "false");
        submitButton.disabled = false;
        submitButton.classList.remove("is-loading");
        submitButton.textContent = idleLabel;
    }
}

const urlForm = document.getElementById("url-form");

if (urlForm) {
    const urlInput = document.getElementById("url-input");
    const urlMessage = document.getElementById("url-message");
    const urlSubmit = urlForm.querySelector('button[type="submit"]');

    urlForm.addEventListener("submit", (event) => {
        event.preventDefault();

        runAnalysis({
            endpoint: "/api/analyze/url",
            body: { url: urlInput.value.trim() },
            fallbackMessage: "URL analysis failed. Please try again.",
            kind: "url",
            progressText: "Analyzing URL structure...",
            container: urlMessage,
            input: urlInput,
            submitButton: urlSubmit,
        });
    });
}

const emailForm = document.getElementById("email-form");

if (emailForm) {
    const emailInput = document.getElementById("email-input");
    const emailMessage = document.getElementById("email-message");
    const emailSubmit = emailForm.querySelector('button[type="submit"]');

    emailForm.addEventListener("submit", (event) => {
        event.preventDefault();

        runAnalysis({
            endpoint: "/api/analyze/email",
            body: { email: emailInput.value },
            fallbackMessage: "Email analysis failed. Please try again.",
            kind: "email",
            progressText: "Analyzing email text...",
            container: emailMessage,
            input: emailInput,
            submitButton: emailSubmit,
        });
    });
}

// ---------------------------------------------------------------------
// Analysis history
// ---------------------------------------------------------------------

// Opens the in-page confirmation dialog and resolves to true only
// when the user explicitly confirms the deletion.
function confirmDelete(recordId) {
    const dialog = document.getElementById("confirm-dialog");

    // Fallback for browsers without <dialog> support.
    if (!dialog || typeof dialog.showModal !== "function") {
        return Promise.resolve(
            window.confirm(`Delete analysis record ${recordId}? This cannot be undone.`)
        );
    }

    const confirmText = document.getElementById("confirm-text");
    confirmText.textContent =
        `This removes analysis record ${recordId}. The metadata cannot be recovered.`;

    return new Promise((resolve) => {
        dialog.addEventListener(
            "close",
            () => resolve(dialog.returnValue === "confirm"),
            { once: true }
        );

        dialog.showModal();
    });
}

function createSvgElement(name, attributes) {
    const element = document.createElementNS("http://www.w3.org/2000/svg", name);

    Object.entries(attributes).forEach(([key, value]) => {
        element.setAttribute(key, value);
    });

    return element;
}

function createDeleteButton(recordId, onDeleted) {
    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "action-button danger delete-history-button";
    deleteButton.setAttribute("aria-label", `Delete analysis record ${recordId}`);

    const trashIcon = createSvgElement("svg", {
        width: "15",
        height: "15",
        viewBox: "0 0 24 24",
        fill: "none",
        stroke: "currentColor",
        "stroke-width": "2",
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
        "aria-hidden": "true",
        class: "button-icon",
    });

    trashIcon.appendChild(createSvgElement("path", { d: "M3 6h18" }));
    trashIcon.appendChild(
        createSvgElement("path", {
            d: "M8 6V4h8v2m-11 0 1 14h12l1-14M10 11v5m4-5v5",
        })
    );

    const deleteLabel = document.createElement("span");
    deleteLabel.textContent = "Delete";

    deleteButton.append(trashIcon, deleteLabel);

    deleteButton.addEventListener("click", async () => {
        const confirmed = await confirmDelete(recordId);

        if (!confirmed) return;

        deleteButton.disabled = true;

        try {
            const response = await fetch(`/api/history/${recordId}`, {
                method: "DELETE",
            });

            if (!response.ok) {
                throw new Error("Unable to delete record.");
            }

            onDeleted();
        } catch {
            deleteButton.disabled = false;
            onDeleted(
                "Could not delete the record. Please try again."
            );
        }
    });

    return deleteButton;
}

const historyBody = document.getElementById("history-table-body");
const historyStatus = document.getElementById("history-status");
const refreshHistoryButton = document.getElementById("refresh-history");

if (historyBody && historyStatus) {
    async function loadHistory(errorOverride) {
        historyStatus.textContent = "Loading analysis history...";
        historyBody.replaceChildren();

        try {
            const response = await fetch("/api/history");
            const history = await readJson(response);

            if (!response.ok || !Array.isArray(history)) {
                throw new Error("Unable to load analysis history.");
            }

            if (history.length === 0) {
                historyStatus.textContent =
                    "No analyses recorded yet. Run a URL or email analysis to start your history.";
                return;
            }

            historyStatus.textContent =
                errorOverride || `${history.length} recent analysis record(s).`;

            history.forEach((record) => {
                const row = document.createElement("tr");

                const values = [
                    record.id,
                    record.analysis_type.toUpperCase(),
                    new Date(record.analyzed_at).toLocaleString(),
                    `${record.score}/100`,
                    record.severity,
                    record.indicator_count,
                ];

                values.forEach((value) => {
                    const cell = document.createElement("td");
                    cell.textContent = String(value);
                    row.appendChild(cell);
                });

                const actionCell = document.createElement("td");
                actionCell.appendChild(
                    createDeleteButton(record.id, (errorText) => {
                        loadHistory(errorText);
                    })
                );
                row.appendChild(actionCell);

                historyBody.appendChild(row);
            });
        } catch {
            historyStatus.textContent =
                "Could not load history. Please refresh the page and try again.";
        }
    }

    refreshHistoryButton?.addEventListener("click", () => loadHistory());
    loadHistory();
}

// ---------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------

function appendMessageRow(body, colSpan, text, link) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");

    cell.colSpan = colSpan;

    const message = document.createElement("p");
    message.className = "dashboard-empty-text";
    message.textContent = text;
    cell.appendChild(message);

    if (link) {
        const anchor = document.createElement("a");
        anchor.href = link.href;
        anchor.textContent = link.text;
        cell.appendChild(anchor);
    }

    row.appendChild(cell);
    body.appendChild(row);
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
        const data = await readJson(response);

        if (!response.ok || !data) {
            throw new Error("Could not load dashboard data.");
        }

        totalScans.textContent = data.total_scans;
        suspiciousResults.textContent = data.suspicious_results;
        highRiskResults.textContent = data.high_risk_results;

        activityBody.replaceChildren();

        if (!data.recent_activity || data.recent_activity.length === 0) {
            appendMessageRow(
                activityBody,
                6,
                "No analyses recorded yet. Analyze a URL or an email to see activity here.",
                { href: "/url-analyzer", text: "Start with the URL Analyzer" }
            );
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
                const safeSeverity = SEVERITY_LEVELS.map((level) =>
                    level.toLowerCase()
                ).includes(severity)
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

        appendMessageRow(
            activityBody,
            6,
            "Dashboard data is temporarily unavailable. Refresh the page to try again."
        );

        dashboardStatus.textContent = "Unavailable";
        console.error("Dashboard loading error:", error);
    }
}

loadDashboard();
