// POTREBBE ESSERE AGGIORNATO...

const fileViewerOverlay = document.getElementById('fileViewerOverlay');
const fileViewer = document.getElementById('fileViewer');
const fileViewerContent = document.getElementById('fileViewerContent');
const closeBtn = document.getElementById('closeBtn');

function openFileViewer(file, type) {
    if (type === "PNG" || type === "JPG" || type === "JPEG") {
        fileViewerContent.innerHTML = `<img src="/r/${file}" alt="${file}" />`;
    } else if (type === "MP4" || type === "MOV" || type === "MKV" || type === "AVI") {
        fileViewerContent.innerHTML = `
        <video controls>
            <source src="/r/${file}" type="video/mp4">
        </video>
        `;
    } else if (type === "MP3" || type === "WAV" || type === "OGG") {
        fileViewerContent.innerHTML = `
        <audio controls>
            <source src="/r/${file}" type="audio/ogg">
        </audio>
        `;
    } else {
        fileViewerContent.innerHTML = `
        <h3 style="display: flex; align-items: center; justify-content: center;">Invalid file extension.</h3>
        <p>The FilEZ-Viewer 1.0 cannot open this file.<br>Please download or open as RAW to view.</p>
        <center>
            <a href="/r/${file}"><button class="btn btn-primary btn-sm">Download</button></a>
            <a href="/r/${file}?a=False"><button class="btn btn-success btn-sm">View as RAW</button></a>
        </center>
        `;
    }
    
    fileViewerOverlay.classList.add('active');
    fileViewer.classList.add('active');
}

function closeFileViewer() {
    fileViewerOverlay.classList.remove('active');
    fileViewer.classList.remove('active');
    fileViewerContent.innerHTML = '';
}

fileViewerOverlay.addEventListener('click', function(event) {
    if (event.target === this) {
        closeFileViewer();
    }
});




