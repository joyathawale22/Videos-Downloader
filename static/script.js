document.getElementById("downloadBtn").addEventListener("click", startDownload);

function startDownload() {
    let videoUrl = document.getElementById("videoUrl").value;
    let quality = document.getElementById("quality").value;
    let audioOnly = document.getElementById("audioOnly").checked;
    let subtitles = document.getElementById("subtitles").checked;
    let progressBar = document.getElementById("progressBar");
    let statusMessage = document.getElementById("statusMessage");
    let etaDisplay = document.getElementById("eta");
    let speedDisplay = document.getElementById("speed");

    if (!videoUrl) {
        alert("Please enter a valid video URL!");
        return;
    }

    // Reset UI before download starts
    progressBar.style.width = "0%";
    progressBar.innerText = "0%";
    statusMessage.innerText = "⏳ Downloading... Please wait.";
    etaDisplay.innerText = "Time Remaining: Calculating...";
    speedDisplay.innerText = "Speed: 0 Mbps";

    // Start listening for real-time progress updates
    let eventSource = new EventSource("http://127.0.0.1:5000/progress");
    eventSource.onmessage = function (event) {
        let progressData = JSON.parse(event.data.replace("data: ", ""));
        progressBar.style.width = progressData.percentage + "%";
        progressBar.innerText = progressData.percentage + "%";
        etaDisplay.innerText = "Time Remaining: " + progressData.eta;
        speedDisplay.innerText = "Speed: " + progressData.speed + " Mbps";
        
        // Stop event source if download completes
        if (progressData.percentage >= 100) {
            eventSource.close();
        }
    };

    // Send request to Flask API
    fetch("http://127.0.0.1:5000/download", {  
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            url: videoUrl,
            quality: quality,
            audio_only: audioOnly,
            subtitles: subtitles
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            statusMessage.innerText = "✅ Download Complete!";
        } else {
            statusMessage.innerText = "❌ Error: " + data.message;
        }
    })
    .catch(error => {
        console.error("Error:", error);
        statusMessage.innerText = "❌ Failed to connect to server.";
    });
}
