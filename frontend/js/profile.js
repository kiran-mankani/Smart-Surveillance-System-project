// ============================================================
// PROFILE.JS
// Smart Surveillance System
// ============================================================

const API_BASE_URL = "http://127.0.0.1:8000";


// ============================================================
// GET TOKEN
// ============================================================

function getToken() {

    return (
        localStorage.getItem("access_token") ||
        localStorage.getItem("token") ||
        localStorage.getItem("accessToken") ||
        localStorage.getItem("jwtToken")
    );
}


// ============================================================
// LOAD PROFILE
// ============================================================

async function loadProfile() {

    const token = getToken();

    console.log("Profile token:", token);

    if (!token) {

        showToast("Please login first.", "error");
        setTimeout(() => {
            window.location.href = "login.html";
        }, 1500);


        return;
    }


    try {

        console.log("Calling:", API_BASE_URL + "/profile");


        const response = await fetch(
            API_BASE_URL + "/profile",
            {
                method: "GET",

                headers: {
                    "Authorization": "Bearer " + token,
                    "Content-Type": "application/json"
                }
            }
        );


        console.log("Profile response status:", response.status);


        const data = await response.json();

        console.log("Profile response:", data);


        // ====================================================
        // ERROR
        // ====================================================

        if (!response.ok) {

            console.error(
                "Profile API Error:",
                response.status,
                data
            );

            
            showToast(
                "Profile API Error: " +
                (data.detail || "Profile endpoint not found.")
                , "error");

            return;
        }


        // ====================================================
        // USER DATA
        // ====================================================

        const user = data.user || data;


        console.log("User:", user);


        // ====================================================
        // NAME
        // ====================================================

        const profileName =
            document.getElementById("profileName");

        if (profileName) {

            profileName.textContent =
                user.name ||
                user.full_name ||
                user.username ||
                "-";
        }


        // ====================================================
        // EMAIL
        // ====================================================

        const profileEmail =
            document.getElementById("profileEmail");

        if (profileEmail) {

            profileEmail.textContent =
                user.email ||
                "-";
        }


        // ====================================================
        // ACCOUNT STATUS
        // ====================================================

        const profileStatus =
            document.getElementById("profileStatus");

        if (profileStatus) {

            if (
                user.is_active !== undefined
            ) {

                profileStatus.textContent =
                    user.is_active
                        ? "Active"
                        : "Inactive";

            }

            else if (
                user.is_verified !== undefined
            ) {

                profileStatus.textContent =
                    user.is_verified
                        ? "Verified"
                        : "Not Verified";

            }

            else {

                profileStatus.textContent =
                    user.status ||
                    "Active";
            }
        }


        // ====================================================
        // ROLE
        // ====================================================

        const profileRole =
            document.getElementById("profileRole");

        if (profileRole) {

            profileRole.textContent =
                user.role ||
                user.user_role ||
                "User";
        }


        // ====================================================
        // HEADER USER NAME
        // ====================================================

        const headerUser =
            document.querySelector(".header .user");

        if (headerUser) {

            const name =
                user.name ||
                user.full_name ||
                user.username ||
                "User";

            headerUser.textContent =
                `Welcome, ${name} 👋`;
        }


        console.log(
            "Profile loaded successfully."
        );

    }


    catch (error) {

        console.error(
            "Profile Error:",
            error
        );

       
        showToast( "Could not connect to profile API.", "info");
    }
}


// ============================================================
// LOGOUT
// ============================================================

function logout() {

    const confirmLogout =
        confirm(
            "Are you sure you want to logout?"
        );


    if (!confirmLogout) {
        return;
    }


    localStorage.removeItem("access_token");
    localStorage.removeItem("token");
    localStorage.removeItem("accessToken");
    localStorage.removeItem("jwtToken");

    localStorage.removeItem(
        "lastPredictionResult"
    );

    sessionStorage.clear();


    window.location.href =
        "login.html";
}


// ============================================================
// PAGE LOAD
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        console.log(
            "Profile JS loaded successfully."
        );


        loadProfile();


        const logoutBtn =
            document.getElementById(
                "logoutBtn"
            );


        if (logoutBtn) {

            logoutBtn.addEventListener(
                "click",
                logout
            );
        }

    }
);