// FILE LOADER
window.addEventListener('DOMContentLoaded', (event) => {
    const urlParams = new URLSearchParams(window.location.search);
    var location = urlParams.get('location');

    if (!location) {
        location = 'my_files';
    }

    loadFiles(location);
    console.log(location);
});

function loadFiles(location) {
    const url = `http://127.0.0.1:8080/api/get_files?location=${location}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            updateFileTable(data);
        })
        .catch(error => console.error('Error during file loading: ', error));
}

function updateFileTable(files) {
    const fileTableBody = document.querySelector('#file-table tbody');

    fileTableBody.innerHTML = '';

    files.forEach(file => {
        const newRow = document.createElement('tr')
        const file_type = `${file.filename}`.split('.').pop();
        console.log(file_type);
        newRow.innerHTML = `
            <td><a href="#" onclick="openFileViewer(${file.file_code}, '${file_type}')">${file.filename}</a></td>
            <td>${file.upload_date}</td>
            <td>${file.owner}</td>
            <td>${file.location}</td>
            <td>
                <a href="${file.raw_url}"><button class="btn btn-primary btn-sm">Download</button></a>
                <button class="btn btn-primary btn-sm shareBtn" onclick="openShareModal('${file.filename}', '${file.file_code}')">Share</button>
                <button class="btn btn-danger btn-sm">Delete</button>
            </td>
        `;
        fileTableBody.appendChild(newRow);
    });
}

