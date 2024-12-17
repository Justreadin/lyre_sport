document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const nameInput = document.getElementById("name");
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirm_password");

    form.addEventListener("submit", function (event) {
        // Clear previous error messages
        document.querySelectorAll(".error-message").forEach(el => el.remove());

        let hasError = false;

        // Validate Full Name
        if (nameInput.value.trim() === "") {
            showError(nameInput, "Full Name is required.");
            hasError = true;
        }

        // Validate Email
        if (emailInput.value.trim() === "") {
            showError(emailInput, "Email is required.");
            hasError = true;
        } else if (!isValidEmail(emailInput.value)) {
            showError(emailInput, "Enter a valid email address.");
            hasError = true;
        }

        // Validate Password
        if (passwordInput.value.trim() === "") {
            showError(passwordInput, "Password is required.");
            hasError = true;
        } else if (passwordInput.value.length < 8) {
            showError(passwordInput, "Password must be at least 8 characters long.");
            hasError = true;
        }

        // Validate Confirm Password
        if (confirmPasswordInput.value.trim() === "") {
            showError(confirmPasswordInput, "Confirm Password is required.");
            hasError = true;
        } else if (confirmPasswordInput.value !== passwordInput.value) {
            showError(confirmPasswordInput, "Passwords do not match.");
            hasError = true;
        }

        // Prevent form submission if there are errors
        if (hasError) {
            event.preventDefault();
        }
    });

    // Helper Functions
    function showError(input, message) {
        const errorMessage = document.createElement("p");
        errorMessage.textContent = message;
        errorMessage.className = "error-message text-red-600 text-sm mt-1";
        input.insertAdjacentElement("afterend", errorMessage);
    }

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
});

