const form = document.getElementById("resetPasswordForm");
console.log("Reset Password JS Loaded");
const newPassword = document.getElementById("newPassword");
const confirmPassword = document.getElementById("confirmPassword");

const toggleNewPassword = document.getElementById("toggleNewPassword");
const toggleConfirmPassword = document.getElementById("toggleConfirmPassword");


// ==============================
// Show / Hide New Password
// ==============================

toggleNewPassword.addEventListener("click", () => {

    if (newPassword.type === "password") {

        newPassword.type = "text";
        toggleNewPassword.innerHTML = `
        <svg width="20px" height="20px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 5C5.63636 5 2 12 2 12C2 12 5.63636 19 12 19C18.3636 19 22 12 22 12C22 12 18.3636 5 12 5Z" stroke="#000000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="#000000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>`
        
    } else {
        
        newPassword.type = "password";
        toggleNewPassword.innerHTML = `<svg width="20px" height="20px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2L22 22" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M6.71277 6.7226C3.66479 8.79527 2 12 2 12C2 12 5.63636 19 12 19C14.0503 19 15.8174 18.2734 17.2711 17.2884M11 5.05822C11.3254 5.02013 11.6588 5 12 5C18.3636 5 22 12 22 12C22 12 21.3082 13.3317 20 14.8335" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M14 14.2362C13.4692 14.7112 12.7684 15.0001 12 15.0001C10.3431 15.0001 9 13.657 9 12.0001C9 11.1764 9.33193 10.4303 9.86932 9.88818" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>`

    }

});


// ==============================
// Show / Hide Confirm Password
// ==============================

toggleConfirmPassword.addEventListener("click", () => {

    if (confirmPassword.type === "password") {

        confirmPassword.type = "text";
        toggleConfirmPassword.innerHTML = `
        <svg width="20px" height="20px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 5C5.63636 5 2 12 2 12C2 12 5.63636 19 12 19C18.3636 19 22 12 22 12C22 12 18.3636 5 12 5Z" stroke="#000000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="#000000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>`
        
    } else {
        
        confirmPassword.type = "password";
        toggleConfirmPassword.innerHTML = `<svg width="20px" height="20px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2L22 22" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M6.71277 6.7226C3.66479 8.79527 2 12 2 12C2 12 5.63636 19 12 19C14.0503 19 15.8174 18.2734 17.2711 17.2884M11 5.05822C11.3254 5.02013 11.6588 5 12 5C18.3636 5 22 12 22 12C22 12 21.3082 13.3317 20 14.8335" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M14 14.2362C13.4692 14.7112 12.7684 15.0001 12 15.0001C10.3431 15.0001 9 13.657 9 12.0001C9 11.1764 9.33193 10.4303 9.86932 9.88818" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>`

    }

});


// ==============================
// Reset Password
// ==============================

form.addEventListener("submit", async function(e) {

    e.preventDefault();

    const password = newPassword.value;
    const confirm = confirmPassword.value;

    console.log("New Password:", password);
    console.log("Confirm Password:", confirm);


    // ==============================
    // Check Empty
    // ==============================

    if (password === "" || confirm === "") {

        showToast("Please enter both passwords.", "error");
        return;

    }


    // ==============================
    // Check Password Match
    // ==============================

    if (password !== confirm) {

        showToast("Passwords do not match.", "error");
        return;

    }


    // ==============================
    // Password Strength
    // ==============================

    const strongPassword =
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

    if (!strongPassword.test(password)) {

        showToast(
             "Password must contain:\n" +
            "- At least 8 characters\n" +
            "- 1 uppercase letter (A-Z)\n" +
            "- 1 lowercase letter (a-z)\n" +
            "- 1 number (0-9)\n" +
            "- 1 special character (@ $ ! % * ? &)"
            , "info");

        return;

    }


    // ==============================
    // Get Email
    // ==============================

    const email = localStorage.getItem("reset_email");

    if (!email) {

        showToast("Email not found. Please restart Forgot Password.", "error");

        return;

    }


    // ==============================
    // Backend
    // ==============================

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/set-new-password",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    email: email,
                    new_password: password
                })
            }
        );


        const data = await response.json();

        console.log("Backend Response:", data);

        showToast(data.message, "success");


        // ==============================
        // Password Updated
        // ==============================

        if (
            response.ok &&
            data.message === "Password updated successfully"
        ) {

            localStorage.removeItem("reset_email");

            window.location.href = "login.html";

        }

    } catch (error) {

        console.error("Error:", error);

        showToast("Cannot connect to backend.", "error");

    }

});