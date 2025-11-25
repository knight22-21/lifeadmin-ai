document.getElementById("upload-btn").onclick = async () => {

    const file = document.getElementById("file-input").files[0];
    if (!file) return alert("Please select a file.");

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

        // ACTIONS PERFORMED SUMMARY
        const actionsCard = document.getElementById("actions-card");

        const email = json?.result?.email_result;
        const todoist = json?.result?.todoist_task;
        const logged = json?.result?.logged;

        let actionsHTML = "";

        // Check for Email result
        if (email?.status_code === 202) {
            actionsHTML += "Email notification sent<br>";
        } else if (email) {
            actionsHTML += "Email failed or skipped<br>";
        }

        // Check for Todoist task result
        if (todoist?.url) {
            actionsHTML += `Todoist task created: <a href="${todoist.url}" target="_blank">View Task</a><br>`;
        } else if (todoist) {
            actionsHTML += "Todoist task NOT created<br>";
        }

        // Logging status
        if (logged) {
            actionsHTML += "Logged to Supabase<br>";
        } else if (json?.result?.logged === false) {
            actionsHTML += "Logging failed<br>";
        }

        actionsCard.innerHTML = actionsHTML;

    } catch (error) {
        document.getElementById("loader").classList.add("hidden");
        alert("Error: " + error);
    }
};
