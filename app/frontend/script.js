const fileInput = document.getElementById("file-input");
const uploadBtn = document.getElementById("upload-btn");
const uploadArea = document.getElementById("upload-area");

// -------------------------
// DRAG & DROP SUPPORT
// -------------------------
uploadArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadArea.style.background = "rgba(255,255,255,0.12)";
});

uploadArea.addEventListener("dragleave", () => {
    uploadArea.style.background = "rgba(255,255,255,0.05)";
});

uploadArea.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadArea.style.background = "rgba(255,255,255,0.05)";
    fileInput.files = e.dataTransfer.files;
});

// -------------------------
// MAIN UPLOAD HANDLER
// (YOUR ORIGINAL LOGIC)
// -------------------------
document.getElementById("upload-btn").onclick = async () => {

    const file = document.getElementById("file-input").files[0];
    if (!file) {
        showToast("Please select a file.", "error");
        return;
    }

    document.getElementById("loader").classList.remove("hidden");
    document.getElementById("result-container").classList.add("hidden");

    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await fetch("/process", {
            method: "POST",
            body: formData
        });

        const json = await res.json();

        document.getElementById("loader").classList.add("hidden");
        document.getElementById("result-container").classList.remove("hidden");

        // -------------------------
        // ACTIONS PERFORMED SUMMARY
        // (EXACT ORIGINAL LOGIC)
        // -------------------------
        const actionsCard = document.getElementById("actions-card");

        const email = json?.result?.email_result;
        const todoist = json?.result?.todoist_task;
        const logged = json?.result?.logged;

        let actionsHTML = "";

        // Email result
        if (email?.status_code === 202) {
            actionsHTML += "Email notification sent<br>";
        } else if (email) {
            actionsHTML += "Email failed or skipped<br>";
        }

        // Todoist task result
        if (todoist?.url) {
            actionsHTML += `Todoist task created: <a href="${todoist.url}" target="_blank">View Task</a><br>`;
        } else if (todoist) {
            actionsHTML += "Todoist task NOT created<br>";
        }

        // Logging result
        if (logged) {
            actionsHTML += "Logged to Database<br>";
        } else if (json?.result?.logged === false) {
            actionsHTML += "Logging failed<br>";
        }

        actionsCard.innerHTML = actionsHTML;

        showToast("File processed successfully!", "success");

    } catch (error) {
        document.getElementById("loader").classList.add("hidden");
        showToast("Error: " + error.message, "error");
    }
};

// -------------------------
// TOAST SYSTEM
// -------------------------
function showToast(message, type = "success") {
    const toast = document.createElement("div");
    toast.classList.add("toast", type);

    toast.innerText = message;

    const container = document.getElementById("toast-container");
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 4000); // auto-remove
}
