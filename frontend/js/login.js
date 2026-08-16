// ===============================
// Show / Hide Password
// ===============================

// ===============================
// Show / Hide Password
// ===============================

const togglePassword = document.getElementById("togglePassword");
const password = document.getElementById("password");

togglePassword.addEventListener("click", () => {

    if (password.type === "password") {
        password.type = "text";
togglePassword.innerHTML = `
<svg width="20px" height="20px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M12 5C5.63636 5 2 12 2 12C2 12 5.63636 19 12 19C18.3636 19 22 12 22 12C22 12 18.3636 5 12 5Z" stroke="#000000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="#000000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>`
} else {
    password.type = "password";
    togglePassword.innerHTML = `<svg width="20px" height="20px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2L22 22" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M6.71277 6.7226C3.66479 8.79527 2 12 2 12C2 12 5.63636 19 12 19C14.0503 19 15.8174 18.2734 17.2711 17.2884M11 5.05822C11.3254 5.02013 11.6588 5 12 5C18.3636 5 22 12 22 12C22 12 21.3082 13.3317 20 14.8335" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M14 14.2362C13.4692 14.7112 12.7684 15.0001 12 15.0001C10.3431 15.0001 9 13.657 9 12.0001C9 11.1764 9.33193 10.4303 9.86932 9.88818" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>`
    }

});


// ===============================
// Login Form
// ===============================

const loginForm = document.getElementById("loginForm");

loginForm.addEventListener("submit", async (e) => {

    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const passwordValue = document.getElementById("password").value.trim();

    if (email === "" || passwordValue === "") {

        showToast("Please fill all fields.", "error");
        return;

    }

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/login",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    email: email,
                    password: passwordValue

                })
            }
        );

        const data = await response.json();

        console.log("Login Response:", data);

        if (!response.ok) {

            showToast(data.detail || data.message, "info");
            return;

        }

        // Save JWT Token
        localStorage.setItem(
            "token",
            data.access_token
        );

        // Save Email
        localStorage.setItem(
            "email",
            email
        );

        showToast(
            data.message || "Login Successful",
            "success"
        );

        setTimeout(() => {
            window.location.href = "dashboard.html";
        }, 1500);

    }

    catch (error) {

        console.error(error);

        showToast("Cannot connect to backend.", "info");

    }

});