document.getElementById("upload-btn").onclick = async () => {
    const file = document.getElementById("file-input").files[0];
    if (!file) return alert("Please select a file first.");

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/process", {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    const box = document.getElementById("response-box");
    box.style.display = "block";
    box.innerText = JSON.stringify(data, null, 2);
};
