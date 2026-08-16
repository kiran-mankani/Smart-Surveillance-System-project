// ============================================================
// HISTORY.JS
// ============================================================

const API_BASE_URL = "http://127.0.0.1:8000";


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

    const token = getToken();

    if (!token) {

        showToast(
            "Please login first.",
            "info"
        );


        return;
    }


    try {

        const response = await fetch(
            API_BASE_URL + "/history",
            {
                method: "GET",

                headers: {
                    "Authorization":
                        "Bearer " + token
                }
            }
        );


        const data =
            await response.json();


        console.log(
            "History:",
            data
        );


        if (!response.ok) {

            showToast(data.detail || "Could not load history.", "error");

            return;
        }


        const table =
            document.getElementById(
                "historyTable"
            );


        if (!table) return;


        table.innerHTML = "";


        if (
            !data.history ||
            data.history.length === 0
        ) {

            table.innerHTML = `
                <tr>
                    <td colspan="4"
                        style="text-align:center;">
                        No prediction history available.
                    </td>
                </tr>
            `;

            return;
        }


        data.history.forEach(
            function (item) {

                let confidence =
                    item.confidence;


                if (
                    confidence !== null &&
                    confidence !== undefined
                ) {

                    confidence =
                        parseFloat(confidence);


                    if (!isNaN(confidence)) {

                        if (confidence <= 1) {

                            confidence =
                                confidence * 100;
                        }


                        confidence =
                            confidence.toFixed(2) +
                            "%";
                    }

                } else {

                    confidence = "N/A";
                }


                let date =
                    item.prediction_time || "-";


                if (date !== "-") {

                    date =
                        new Date(date)
                            .toLocaleString();
                }


                table.innerHTML += `

                    <tr>

                        <td>
                            ${item.video_name || "-"}
                        </td>

                        <td>
                            ${item.predicted_class || "-"}
                        </td>

                        <td>
                            ${confidence}
                        </td>

                        <td>
                            ${item.status || "-"}
                        </td>

                    </tr>

                `;
            }
        );

    }


    catch (error) {

        console.error(
            "History Error:",
            error
        );
    }
}


// ============================================================
// LOGOUT
// ============================================================

function logout() {

    if (
        confirm(
            "Are you sure you want to logout?"
        )
    ) {

        localStorage.clear();

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