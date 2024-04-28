// DRAG AND DROP

var fileDropOverlay = document.getElementById('file-drop-overlay');

document.addEventListener('dragover', function(event) { // DETECTS DRAGOVER
    event.preventDefault();

    console.log("Detected dragover")
    fileDropOverlay.style.display = 'block';
});

        //document.addEventListener('dragleave', function(event) {
        //    event.preventDefault();
        //    
        //    fileDropOverlay.style.display = 'none';
        //});

document.addEventListener('drop', function(event) {
    event.preventDefault();

    fileDropOverlay.style.display = 'none';

    var files = event.dataTransfer.files;
            
    console.log('File dropped.')
    uploadFiles(files)
});

function uploadFiles(files) {
    var formData = new FormData();

    var uploadLocation = getUrlParamater('location');

    if (uploadLocation == "trash") {
        alert("You cannot upload files here.");
        window.location.href = "/dashboard?location=my_files";
    }

    formData.append('location', uploadLocation);

    for (var i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/upload_files', true);
    xhr.onload = function() {
        if (xhr.status === 200) {
            console.log("200 OK (Uploaded)")
            location.reload();
        } else {
            console.error("Failed: ", xhr.status, xhr.error_text);
            alert("Failed to upload files.");
        }
    };
    xhr.send(formData);
}

function getUrlParamater(name) {
    name = name.replace(/[\][]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '))
}