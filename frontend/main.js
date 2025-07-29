//  Define task card elements
function createTaskCard(description = "", assignee = "", status = "To-Do") {
    const card = document.createElement("div");
    card.className = "task-card";

    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "x";
    deleteBtn.className = "delete-btn";
    deleteBtn.onclick = () => {
        card.remove();
        const hasCards = document.querySelectorAll(".task-card").length > 0;
        document.getElementById("add-task").style.display = hasCards ? "inline-block" : "none";
        document.getElementById("send-trello").disabled = !hasCards;
    };

    const descLabel = document.createElement("label");
    descLabel.textContent = "Description";

    const descInput = document.createElement("input");
    descInput.type = "text";
    descInput.name = "description";
    descInput.className = "task-input";
    descInput.value = description;

    // Container for assignee and status side by side
    const flexRow = document.createElement("div");
    flexRow.className = "flex-row";

    // Assignee
    const assigneeGroup = document.createElement("div");
    assigneeGroup.className = "flex-item";
    const assigneeLabel = document.createElement("label");
    assigneeLabel.textContent = "Assignee";
    const assigneeInput = document.createElement("input");
    assigneeInput.type = "text";
    assigneeInput.name = "assignee";
    assigneeInput.className = "task-input";
    assigneeInput.value = assignee;
    assigneeGroup.appendChild(assigneeLabel);
    assigneeGroup.appendChild(assigneeInput);

    // Status dropdown
    const statusGroup = document.createElement("div");
    statusGroup.className = "flex-item";
    const statusLabel = document.createElement("label");
    statusLabel.textContent = "Status";
    const statusSelect = document.createElement("select");
    statusSelect.name = "status";
    statusSelect.className = "task-input";
    ["To-Do", "Doing", "Done"].forEach(option => {
        const opt = document.createElement("option");
        opt.value = option;
        opt.textContent = option;
        if (option === status) opt.selected = true;
        statusSelect.appendChild(opt);
    });
    statusGroup.appendChild(statusLabel);
    statusGroup.appendChild(statusSelect);

    flexRow.appendChild(assigneeGroup);
    flexRow.appendChild(statusGroup);

    card.appendChild(deleteBtn);
    card.appendChild(descLabel);
    card.appendChild(descInput);
    card.appendChild(flexRow);

    document.getElementById("tasks-container").appendChild(card);
}

//  Transcribe audio and extract tasks
document.getElementById("run-pipeline").addEventListener("click", async () => {
    const transcriptOut = document.getElementById("transcript-output");
    transcriptOut.style.display = "none";
    document.getElementById("send-trello").disabled = true;
    document.getElementById("spinner").style.display = "flex";

    try {
        const useCloud = document.querySelector('input[name="recordingType"]:checked').value === "cloud";

        const res = await fetch("/api/transcribe_extract", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ use_cloud: useCloud }),
        });
        
        const data = await res.json();
        if (data.error) throw new Error(data.error);
  
        transcriptOut.textContent = `Transcript:\n\n${data.transcript}`;

        const container = document.getElementById("tasks-container");
        container.innerHTML = "";

        if (!Array.isArray(data.tasks)) {
            throw new Error("No tasks returned from backend.");
        }

        data.tasks.forEach(task => {
            createTaskCard(
                task.description || "",
                task.assignee || "",
                task.status || "To-Do"
            );
        });

        document.getElementById("spinner").style.display = "none";
        transcriptOut.style.display = "block";  

        window.latestTasks = data.tasks;
        document.getElementById("send-trello").disabled = false;
        document.getElementById("add-task").style.display = "inline-block";
    } catch (err) {
        transcriptOut.textContent = `[ERROR]\t\t${err.message}`;
    } finally {
        document.getElementById("spinner").style.display = "none";
        transcriptOut.style.display = "block";
    }
});

//  Submit tasks to Trello
document.getElementById("send-trello").addEventListener("click", async () => {
    const updatedTasks = [];

    document.querySelectorAll(".task-card").forEach(card => {
        const desc = card.querySelector("input[name='description']").value.trim();
        const assignee = card.querySelector("input[name='assignee']").value.trim();
        const status = card.querySelector("select[name='status']").value.trim();

        updatedTasks.push({
            description: desc,
            assignee: assignee,
            status: status || "To-Do"
        });
    });

    try {
        const res = await fetch("/api/send_to_trello", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ tasks: updatedTasks }),
        });

        const data = await res.json();

        if (data.error) {
            console.error("[ERROR]\t\tError sending to Trello:", data.error);
        } else {
            console.log("[SUCCESS]\tSent to Trello:", data.results);
            alert("✅ Sent to Trello!");
            location.reload();
        }

        document.getElementById("send-trello").disabled = true;
    } catch (err) {
        console.error("[ERROR]\t\tTrello submission failed:", err);
    }
});

//  Add task manually
document.getElementById("add-task").addEventListener("click", () => {
    createTaskCard();
});