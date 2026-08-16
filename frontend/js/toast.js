// ==============================
// Toast Notifications
// ==============================

function showToast(message, type = "success") {

    let icon = "✓";
    let background = "linear-gradient(135deg, #16a34a, #22c55e)";

    if (type === "error") {
        icon = "✕";
        background = "linear-gradient(135deg, #dc2626, #ef4444)";
    }

    if (type === "warning") {
        icon = "!";
        background = "linear-gradient(135deg, #d97706, #f59e0b)";
    }

    if (type === "info") {
        icon = "";
        background = "linear-gradient(135deg, #2563eb, #3b82f6)";
    }

    Toastify({
        text: `${icon}  ${message}`,

        duration: 3500,

        close: true,

        gravity: "top",

        position: "right",

        stopOnFocus: true,

        offset: {
            x: 20,
            y: 20
        },

        style: {
            background: background,
            borderRadius: "10px",
            padding: "14px 18px",
            fontSize: "14px",
            fontWeight: "500",
            boxShadow: "0 8px 25px rgba(0, 0, 0, 0.25)"
        }

    }).showToast();
}