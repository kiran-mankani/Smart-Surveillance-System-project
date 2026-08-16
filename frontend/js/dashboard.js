// ============================================================
// DASHBOARD.JS
// Smart Surveillance System
// ============================================================

const API_BASE_URL = "http://localhost:8000";


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
// DISPLAY RESULT
// ============================================================

function setResult(video, prediction, confidence, status) {
    const videoName = document.getElementById("videoName");
    const predictionBox = document.getElementById("prediction");
    const confidenceBox = document.getElementById("confidence");
    const statusBox = document.getElementById("status");

    if (videoName) videoName.textContent = video || "-";
    if (predictionBox) predictionBox.textContent = prediction || "-";
    if (confidenceBox) confidenceBox.textContent = confidence || "-";
    if (statusBox) statusBox.textContent = status || "-";

    // Save result in localStorage
    const result = {
        video: video || "-",
        prediction: prediction || "-",
        confidence: confidence || "-",
        status: status || "-"
    };

    localStorage.setItem("lastPredictionResult", JSON.stringify(result));
}


// ============================================================
// LOAD LAST PREDICTION RESULT
// ============================================================

function loadLastPredictionResult() {
    const savedResult = localStorage.getItem("lastPredictionResult");

    if (!savedResult) return;

    try {
        const result = JSON.parse(savedResult);

        const videoName = document.getElementById("videoName");
        const predictionBox = document.getElementById("prediction");
        const confidenceBox = document.getElementById("confidence");
        const statusBox = document.getElementById("status");

        if (videoName) videoName.textContent = result.video || "-";
        if (predictionBox) predictionBox.textContent = result.prediction || "-";
        if (confidenceBox) confidenceBox.textContent = result.confidence || "-";
        if (statusBox) statusBox.textContent = result.status || "-";

        console.log("Last prediction result restored.");
    } catch (error) {
        console.error("Could not restore prediction result:", error);
    }
}


// ============================================================
// FORMAT CONFIDENCE
// ============================================================

function formatConfidence(value) {
    if (value === null || value === undefined || value === "") {
        return "N/A";
    }

    let confidence = parseFloat(value);

    if (isNaN(confidence)) {
        return value;
    }

    // Backend agar 0.95 bheje to 95.00% banega
    if (confidence <= 1) {
        confidence = confidence * 100;
    }

    return confidence.toFixed(2) + "%";
}


// ============================================================
// UPLOAD + PREDICT
// ============================================================
// NOTE: This function is async and awaits the fetch + json parse
// before doing anything else. Nothing here can trigger a page
// navigation. If your result was disappearing, the cause was
// almost certainly outside this function (duplicate listeners,
// a <form> ancestor causing a real submit, or a second copy of
// this script being loaded). See the guarded listener below.
// ============================================================

async function uploadAndPredict(event) {
    if (event) {
        event.preventDefault();
    }

    // ========================================================
    // GET VIDEO INPUT
    // ========================================================

    const fileInput = document.getElementById("videoFile");

    if (!fileInput) {
        console.error("videoFile element not found.");
        showToast("Video input not found.", "error");
        return;
    }

    // ========================================================
    // CHECK FILE
    // ========================================================

    if (!fileInput.files || fileInput.files.length === 0) {
        showToast("Please select a video first.", "info");
        return;
    }

    const file = fileInput.files[0];

    // ========================================================
    // GET TOKEN
    // ========================================================

    const token = getToken();

    if (!token) {
        showToast("Login token not found. Please login again.", "error");
        return;
    }

    // ========================================================
    // SHOW PROCESSING
    // ========================================================

    setResult(file.name, "Predicting...", "Processing...", "Processing...");

    // ========================================================
    // DISABLE BUTTON WHILE REQUEST IS IN FLIGHT
    // (prevents double-submit if user double-clicks)
    // ========================================================

    const uploadButton = document.getElementById("uploadBtn");
    if (uploadButton) uploadButton.disabled = true;

    // ========================================================
    // FORM DATA
    // ========================================================

    const formData = new FormData();
    formData.append("file", file);

    // ========================================================
    // API REQUEST
    // ========================================================

    try {
        console.log("Sending request:", API_BASE_URL + "/predict");

        const response = await fetch(API_BASE_URL + "/predict", {
            method: "POST",
            headers: {
                "Authorization": "Bearer " + token
            },
            body: formData
        });

        console.log("Response Status:", response.status);

        // ====================================================
        // READ RESPONSE
        // ====================================================

        let data;

        try {
            data = await response.json();
        } catch (jsonError) {
            console.error("Backend did not return valid JSON:", jsonError);
            setResult(file.name, "ERROR", "N/A", "Prediction Failed");
            showToast("Backend returned an invalid response.", "error");
            return;
        }

        console.log(data);

        // ====================================================
        // BACKEND ERROR
        // ====================================================

        if (!response.ok) {
            console.error("========== PREDICTION API ERROR ==========");
            console.error("HTTP Status:", response.status);
            console.error("Backend Response:", data);
            console.error("===========================================");

            setResult(file.name, "ERROR", "N/A", "Prediction Failed");

            showToast(
                "Prediction Failed!\n\n" +
                "Backend Error:\n" +
                (data.detail || data.message || "Unknown backend error")
                , "error");

            return;
        }

        // ====================================================
        // VIDEO NAME
        // ====================================================

        const video =
            data.video ||
            data.video_name ||
            data.filename ||
            data.file_name ||
            data.name ||
            file.name;

        // ====================================================
        // PREDICTED ACTIVITY
        // ====================================================

        const prediction =
            data.predicted_class ||
            data.prediction ||
            data.predicted_activity ||
            data.activity ||
            data.label ||
            data.class ||
            data.predictedClass ||
            "N/A";

        // ====================================================
        // CONFIDENCE
        // ====================================================

        const confidence = formatConfidence(data.confidence);

        // ====================================================
        // STATUS
        // ====================================================

        const status =
            data.success === false ? "Prediction Failed" : "Prediction Successful";

        // ====================================================
        // DISPLAY RESULT
        // ====================================================

        setResult(video, prediction, confidence, status);

        console.log("Prediction displayed successfully.");
        console.log("Prediction:", prediction);
        console.log("Confidence:", confidence);
        console.log("Status:", status);

        // ====================================================
        // UPDATE DASHBOARD STATS
        // ====================================================

        await loadDashboardStats();

    } catch (error) {
        console.error("PREDICTION ERROR:", error);

        setResult(file.name, "ERROR", "N/A", "Prediction Failed");
        
        showToast("Could not connect to backend.\n\nMake sure FastAPI is running.", "info");
    } finally {
        if (uploadButton) uploadButton.disabled = false;
    }
}


// ============================================================
// DASHBOARD STATS
// ============================================================

async function loadDashboardStats() {
    const token = getToken();

    if (!token) {
        console.log("No token. Stats skipped.");
        return;
    }

    try {
        const response = await fetch(API_BASE_URL + "/dashboard-stats", {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const data = await response.json();

        console.log("Dashboard Stats:", data);

        if (!response.ok) {
            console.error("Dashboard stats failed:", data);
            return;
        }

        const totalVideos = document.getElementById("totalVideos");
        if (totalVideos) totalVideos.textContent = data.total_videos ?? 0;

        const totalPredictions = document.getElementById("totalPredictions");
        if (totalPredictions) totalPredictions.textContent = data.total_predictions ?? 0;

        const accuracy = document.getElementById("accuracy");
        if (accuracy) {
            accuracy.textContent =
                data.accuracy !== null && data.accuracy !== undefined
                    ? data.accuracy + "%"
                    : "--";
        }

        const todayUploads = document.getElementById("todayUploads");
        if (todayUploads) todayUploads.textContent = data.today_uploads ?? 0;

    } catch (error) {
        console.error("Dashboard Stats Error:", error);
    }
}


// ============================================================
// LOGOUT
// ============================================================

function logout() {
    console.log("Logout clicked");

    const confirmLogout = confirm("Are you sure you want to logout?");

    if (!confirmLogout) return;

    localStorage.removeItem("access_token");
    localStorage.removeItem("token");
    localStorage.removeItem("accessToken");
    localStorage.removeItem("jwtToken");
    localStorage.removeItem("lastPredictionResult");

    sessionStorage.clear();

    console.log("Logged out successfully.");

    window.location.href = "login.html";
}


// ============================================================
// PAGE LOAD
// ============================================================
// GUARD: if this script ever gets included twice on the page
// (duplicate <script> tag, cached + fresh copy, a bundler
// re-injecting it, etc.) this flag stops a second set of
// listeners from being attached. Duplicate listeners were the
// most likely cause of your result "flashing and disappearing" —
// two uploadAndPredict() calls firing per click, racing each
// other, with the second (still on "Processing...") overwriting
// the first's real result.
// ============================================================

if (!window.__dashboardJsInitialized) {
    window.__dashboardJsInitialized = true;

    document.addEventListener("DOMContentLoaded", function () {
        console.log("Dashboard JS loaded successfully.");

        // ====================================================
        // LOAD DASHBOARD STATS
        // ====================================================

        loadDashboardStats();

        // ====================================================
        // LOAD LAST PREDICTION
        // ====================================================

        loadLastPredictionResult();

        // ====================================================
        // UPLOAD BUTTON
        // ====================================================

        const uploadButton = document.getElementById("uploadBtn");

        if (uploadButton) {
            console.log("Upload & Predict button found.");

            uploadButton.addEventListener("click", function (event) {
                event.preventDefault();
                event.stopPropagation();
                uploadAndPredict(event);
            });
        } else {
            console.error("Upload button NOT found.");
        }

        // ====================================================
        // LOGOUT BUTTON
        // ====================================================

        const logoutButton = document.getElementById("logoutBtn");

        if (logoutButton) {
            console.log("Logout button found.");
            logoutButton.onclick = logout;
        } else {
            console.error("Logout button NOT found.");
        }
    });
} else {
    console.warn("dashboard.js was loaded more than once — skipping duplicate init.");
}