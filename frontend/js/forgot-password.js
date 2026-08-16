const forgotForm = document.getElementById("forgotForm");

forgotForm.addEventListener("submit", async (e) => {

    e.preventDefault();

    const email = document.getElementById("email").value.trim();

    if (email === "") {
        showToast("Please enter your email.", "info");
        return;
    }

    // ==========================
    // Backend API
    // ==========================

    try {

        const response = await fetch("http://127.0.0.1:8000/forgot-password", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email: email
            })
        });

        const data = await response.json();

        console.log("Response:", data);

        if (response.ok) {

            showToast(data.message, "success");

            localStorage.setItem("email", email);

            window.location.href = "verify-reset-otp.html";

        } else {

            showToast(data.detail || "Something went wrong.", "error");

        }

    } catch (error) {

        console.error("Error:", error);

        showToast("Cannot connect to backend.", "info");

    }

});