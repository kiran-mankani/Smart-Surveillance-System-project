const verifyForm = document.getElementById("verifyForm");

verifyForm.addEventListener("submit", async (e) => {

    e.preventDefault();

    const otp = document.getElementById("otp").value.trim();
    const email = localStorage.getItem("email");

    if (otp.length !== 6) {
        showToast("Please enter a valid 6-digit OTP.", "error");
        return;
    }

    if (!email) {
        showToast("Email not found.", "error");
        return;
    }

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/verify-email",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: email,
                    otp: otp
                })
            }
        );

        const data = await response.json();

        console.log("Backend Response:", data);

        if (data.success === false) {
            showToast(data.message, "error");
            return;
        }

        if (data.success === true) {
            showToast(data.message, "success");
            setTimeout(() => {
                window.location.href = "login.html";
            }, 1500);
            return;
        }

    } catch (error) {

        console.error(error);
        showToast("Cannot connect to backend.", "error");


    }

});
// ==============================
// Resend OTP
// ==============================

document.getElementById("resendOTP").addEventListener("click", async (e) => {

    e.preventDefault();

    try {

        const response = await fetch("http://127.0.0.1:8000/resend-otp", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: localStorage.getItem("email")
            })
        });

        const data = await response.json();

        showToast(data.message, "success");

    } catch (error) {

        console.error(error);
        showToast("Cannot connect to backend.", "error");

    }

});