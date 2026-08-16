// ============================================================
// PREDICTION.JS
// ============================================================

document.addEventListener("DOMContentLoaded", function () {

    console.log("Prediction JS loaded successfully.");

    loadPrediction();

    setupLogout();

});


// ============================================================
// LOAD LAST PREDICTION
// ============================================================

function loadPrediction() {

    const savedPrediction =
        localStorage.getItem("lastPrediction");


    if (!savedPrediction) {

        console.log("No prediction found.");

        document.getElementById("status").textContent =
            "No prediction available.";

        return;
    }


    try {

        const data =
            JSON.parse(savedPrediction);


        console.log(
            "Last Prediction:",
            data
        );


        // ================================
        // VIDEO NAME
        // ================================

        document.getElementById("videoName").textContent =
            data.video_name || "-";


        // ================================
        // ACTIVITY
        // ================================

        document.getElementById("prediction").textContent =
            data.prediction || "-";


        // ================================
        // CONFIDENCE
        // ================================

        document.getElementById("confidence").textContent =
            data.confidence || "-";


        // ================================
        // STATUS
        // ================================

        document.getElementById("status").textContent =
            data.status || "Prediction Successful";


    }

    catch (error) {

        console.error(
            "Prediction loading error:",
            error
        );

    }

}


// ============================================================
// LOGOUT
// ============================================================

function setupLogout() {

    const logoutBtn =
        document.getElementById("logoutBtn");


    if (!logoutBtn) {

        console.error(
            "Logout button not found."
        );

        return;
    }


    logoutBtn.addEventListener(
        "click",
        function () {

            const confirmLogout =
                confirm(
                    "Are you sure you want to logout?"
                );


            if (confirmLogout) {

                localStorage.removeItem(
                    "access_token"
                );

                localStorage.removeItem(
                    "token"
                );

                localStorage.removeItem(
                    "accessToken"
                );

                localStorage.removeItem(
                    "jwtToken"
                );

                sessionStorage.clear();


                window.location.href =
                    "login.html";
            }

        }
    );

}