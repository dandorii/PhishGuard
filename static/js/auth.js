/*
 * Authentication page helpers (login and registration).
 *
 * These scripts only improve the browser experience. The Flask server
 * still validates every submission, including password length and
 * whether the two passwords match.
 */
(function () {
    "use strict";

    var PASSWORD_MIN_LENGTH = 12;

    // Show/hide buttons stay hidden until JavaScript runs, so a page
    // without JavaScript never shows a control that does nothing.
    function setupPasswordToggles() {
        var toggles = document.querySelectorAll("[data-password-toggle]");

        Array.prototype.forEach.call(toggles, function (toggle) {
            var input = document.getElementById(toggle.getAttribute("aria-controls"));

            if (!input) {
                return;
            }

            toggle.hidden = false;

            toggle.addEventListener("click", function () {
                var isVisible = input.type === "text";
                var label = toggle.getAttribute("aria-label");
                var isConfirmField = label.indexOf("confirm") !== -1;
                var noun = isConfirmField ? "confirm password" : "password";

                input.type = isVisible ? "password" : "text";
                toggle.setAttribute("aria-pressed", String(!isVisible));
                toggle.setAttribute(
                    "aria-label",
                    (isVisible ? "Show " : "Hide ") + noun
                );
                toggle.textContent = isVisible ? "Show" : "Hide";
            });
        });
    }

    function setupRegisterFeedback() {
        var form = document.querySelector("[data-register-form]");

        if (!form) {
            return;
        }

        var password = document.getElementById("password");
        var confirm = document.getElementById("confirm_password");
        var hint = document.getElementById("password-hint");
        var matchMessage = document.getElementById("password-match-message");

        if (!password || !confirm || !hint || !matchMessage) {
            return;
        }

        var passwordField = password.closest(".auth-field");
        var confirmField = confirm.closest(".auth-field");

        function passwordsMatch() {
            return password.value === confirm.value;
        }

        function updateLengthHint() {
            var isLongEnough = password.value.length >= PASSWORD_MIN_LENGTH;

            hint.classList.toggle("is-met", isLongEnough);
            passwordField.classList.toggle(
                "is-invalid",
                password.value.length > 0 && !isLongEnough
            );
        }

        function updateMatchMessage() {
            // Stay quiet until the user has typed something in the confirm field.
            if (confirm.value === "") {
                matchMessage.textContent = "";
                matchMessage.classList.remove("is-error", "is-success");
                confirmField.classList.remove("is-invalid");
                confirm.removeAttribute("aria-invalid");
                return;
            }

            if (passwordsMatch()) {
                matchMessage.textContent = "Passwords match.";
                matchMessage.classList.remove("is-error");
                matchMessage.classList.add("is-success");
                confirmField.classList.remove("is-invalid");
                confirm.setAttribute("aria-invalid", "false");
            } else {
                matchMessage.textContent = "Passwords do not match.";
                matchMessage.classList.remove("is-success");
                matchMessage.classList.add("is-error");
                confirmField.classList.add("is-invalid");
                confirm.setAttribute("aria-invalid", "true");
            }
        }

        password.addEventListener("input", function () {
            updateLengthHint();
            updateMatchMessage();
        });

        confirm.addEventListener("input", updateMatchMessage);

        form.addEventListener("submit", function (event) {
            updateLengthHint();
            updateMatchMessage();

            // Stop early when the passwords differ. The server checks again.
            if (!passwordsMatch()) {
                event.preventDefault();
                confirm.focus();
            }
        });
    }

    function init() {
        setupPasswordToggles();
        setupRegisterFeedback();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
