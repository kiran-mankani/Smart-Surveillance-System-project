// ============================================================
// HISTORY.JS
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
// LOAD HISTORY
// ============================================================

async function loadHistory() {

    console.log("Loading prediction history...");

    const historyTable =
        document.getElementById("historyTable");

    if (!historyTable) {

        console.error(
            "historyTable not found."
        );

        return;
    }


    const token = getToken();

    if (!token) {

        historyTable.innerHTML = `
            <tr>
                <td colspan="4"
                    style="text-align:center;">
                    Please login again.
                </td>
            </tr>
        `;

        return;
    }


    try {

        const response = await fetch(
            API_BASE_URL + "/prediction-history",
            {
                method: "GET",

                headers: {
                    "Authorization":
                        "Bearer " + token
                }
            }
        );


        console.log(
            "History Response Status:",
            response.status
        );


        const data =
            await response.json();


        console.log(
            "History Data:",
            data
        );


        if (!response.ok) {

            historyTable.innerHTML = `
                <tr>
                    <td colspan="4"
                        style="text-align:center;">
                        Unable to load history.
                    </td>
                </tr>
            `;

            return;
        }


        const history =
            data.history || [];


        // ====================================================
        // NO HISTORY
        // ====================================================

        if (history.length === 0) {

            historyTable.innerHTML = `
                <tr>
                    <td colspan="4"
                        style="text-align:center;">
                        No prediction history available.
                    </td>
                </tr>
            `;

            return;
        }


        // ====================================================
        // DISPLAY HISTORY
        // ====================================================

        historyTable.innerHTML = "";


        history.forEach(function (item) {

            let confidence =
                item.confidence;


            // Convert decimal confidence
            // Example: 0.5498 -> 54.98%

            if (
                confidence !== null &&
                confidence !== undefined &&
                confidence !== ""
            ) {

                confidence =
                    parseFloat(confidence);


                if (!isNaN(confidence)) {

                    if (confidence <= 1) {

                        confidence =
                            confidence * 100;
                    }


                    confidence =
                        confidence.toFixed(2) + "%";
                }

            } else {

                confidence = "N/A";
            }


            const row =
                document.createElement("tr");


            row.innerHTML = `

                <td>
                    ${item.video_name || "Unknown"}
                </td>

                <td>
                   ${item.predicted_class || "N/A"}
                </td>

                <td>
                    ${confidence}
                </td>

                <td>
                    ${item.status || "Completed"}
                </td>

            `;


            historyTable.appendChild(row);

        });


        console.log(
            "Prediction history displayed successfully."
        );

    }


    catch (error) {

        console.error(
            "History Error:",
            error
        );


        historyTable.innerHTML = `
            <tr>
                <td colspan="4"
                    style="text-align:center;">
                    Could not connect to backend.
                </td>
            </tr>history.forEach(function (item) 
        `;
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


// ============================================================
// PAGE LOAD
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        console.log(
            "History JS loaded successfully."
        );


        loadHistory();


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