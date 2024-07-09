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
            const files = data.files;
            const archiveSize = data.archive_size;
            updateFileTable(files, location, archiveSize);
        })
        .catch(error => console.error('Error during file loading: ', error));
}

function updateFileTable(files, location, archiveSize) {
    console.log(files);
    const fileTableBody = document.querySelector('#file-table tbody');

    fileTableBody.innerHTML = '';
    
    files.forEach(file => {
        const newRow = document.createElement('tr')

        const sizeText = document.getElementById('sizeText')

        sizeText.textContent = `${archiveSize} used of 10GB`

        const file_type_lowercase = `${file.filename}`.split('.').pop();
        const file_type = file_type_lowercase.toUpperCase();
        console.log(file_type);

        if (location == "trash") {
            newRow.innerHTML = `
                <td><a href="#" onclick="alert('You need to restore this file to see it.')">${file.filename}</a></td>
                <td>${file.upload_date}</td>
                <td>${file.owner}</td>
                <td>${file.location}</td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="openRecoverModal('${file.filename}', '${file.file_code}')">Restore</button>
                    <button class="btn btn-danger btn-sm" onclick="openDeleteModal('${file.filename}', '${file.file_code}')">Delete permanently</button>
                </td>
            `;
            fileTableBody.appendChild(newRow);
        } else if (location == "folders") {
            newRow.innerHTML = `
                <td><a href="/dashboard?location=${file.folder_name}">${file.folder_name}</td>
                <td>${file.creation_date}</td> 
                <td>${file.owner}</td>
                <td>Your archive</td>
                <td>
                    ${file.shared === "True" ? `<button class="btn btn-danger btn-sm" onclick="openUnshareModal('${file.filename}', '${file.file_code}')">Unshare</button>&nbsp;<button class="btn btn-success btn-sm" onclick="copyShareLink(${file.file_code})">Copy share link</button>` : `<button class="btn btn-primary btn-sm shareBtn" onclick="openShareModal('${file.filename}', '${file.file_code}')">Share</button>`}
                    <button class="btn btn-danger btn-sm" onclick="openDeleteModal('${file.folder_name}', '${file.foldercode}', 'folder')">Delete permanently</button>
                </td>
            `
            fileTableBody.appendChild(newRow);
        } else {
        newRow.innerHTML = `
            <td><a href="#" onclick="openFileViewer(${file.file_code}, '${file_type}')">${file.filename}</a></td>
            <td>${file.upload_date}</td>
            <td>${file.owner}</td>
            <td>${file.location}</td>
            <td>
                <a href="/r/${file.file_code}"><button class="btn btn-primary btn-sm">Download</button></a>
                ${file.shared === "True" ? `<button class="btn btn-danger btn-sm" onclick="openUnshareModal('${file.filename}', '${file.file_code}')">Unshare</button>&nbsp;<button class="btn btn-success btn-sm" onclick="copyShareLink(${file.file_code})">Copy share link</button>` : `<button class="btn btn-primary btn-sm shareBtn" onclick="openShareModal('${file.filename}', '${file.file_code}')">Share</button>`}
                <button class="btn btn-danger btn-sm" onclick="moveToTrashModal('${file.filename}', '${file.file_code}')">Move to trash</button>
            </td>
        `;
        fileTableBody.appendChild(newRow);
        }
    });
}

