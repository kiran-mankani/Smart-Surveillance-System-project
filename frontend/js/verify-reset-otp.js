const form = document.getElementById("verifyResetOTPForm");

form.addEventListener("submit", async (e) => {

    e.preventDefault();

    const otp = document.getElementById("otp").value.trim();

    if (otp.length !== 6) {

        showToast("Please enter a valid 6-digit OTP.", "error");
        return;

    }

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/verify-reset-otp",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    email: localStorage.getItem("email"),
                    otp: otp
                })
            }
        );

        const data = await response.json();

        if (response.ok && data.message === "OTP verified successfully") {
            localStorage.setItem(
                "reset_email",
                localStorage.getItem("email")
            );

            showToast(data.message, "success");
            setTimeout(() => {
                window.location.href = "reset-password.html";
            }, 1500);


        } else {

            showToast(data.message, "error");

        }

    } catch (error) {

        console.error(error);
        showToast("Cannot connect to backend.", "error");

    }

});


// ==============================
// Resend OTP
// ==============================

document.getElementById("resendOTP").addEventListener("click", function (e) {

    e.preventDefault();

    showToast("Resend OTP API will be connected next.", "info");

});