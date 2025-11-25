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

        // Fill task card
        const parsed = json?.result?.parsed;
        const taskCard = document.getElementById("task-card");

        if (parsed) {
            taskCard.innerHTML = `
                <strong>Task Type:</strong> ${parsed.task_type}<br>
                <strong>Provider:</strong> ${parsed.provider}<br>
                <strong>Amount:</strong> ${parsed.amount}<br>
                <strong>Due Date:</strong> ${parsed.due_date}<br>
                <strong>Reminder:</strong> ${parsed.reminder_days_before} days before<br>
                <strong>Email:</strong> ${parsed.email}
            `;
        } else {
            taskCard.innerHTML = "<i>No structured task data detected.</i>";
        }

        // OCR text
        document.getElementById("ocr-text").innerText =
            json?.result?.ocr_text || "No OCR text.";

        // Debug JSON
        document.getElementById("raw-json").innerText =
            JSON.stringify(json, null, 2);

        // ACTIONS PERFORMED SUMMARY
        const actionsCard = document.getElementById("actions-card");

        const email = json?.result?.email_result;
        const todoist = json?.result?.todoist_task;
        const logged = json?.result?.logged;

        let actionsHTML = "";

        // Check for Email result
        if (email?.status_code === 202) {
            actionsHTML += "✅ Email notification sent<br>";
        } else if (email) {
            actionsHTML += "❌ Email failed or skipped<br>";
        }

        // Check for Todoist task result
        if (todoist?.url) {
            actionsHTML += `✅ Todoist task created: <a href="${todoist.url}" target="_blank">View Task</a><br>`;
        } else if (todoist) {
            actionsHTML += "❌ Todoist task NOT created<br>";
        }

        // Logging status
        if (logged) {
            actionsHTML += "✅ Logged to Supabase<br>";
        } else if (json?.result?.logged === false) {
            actionsHTML += "❌ Logging failed<br>";
        }

        actionsCard.innerHTML = actionsHTML;

    } catch (error) {
        document.getElementById("loader").classList.add("hidden");
        alert("Error: " + error);
    }
};
