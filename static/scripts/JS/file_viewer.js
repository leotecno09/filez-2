//const fileLinks = document.querySelectorAll('.fileLink');
const fileViewer = document.getElementById('fileViewer');

//fileLinks.forEach(function(link) {
//    link.addEventListener('click', function(event) {
//        event.preventDefault();
//        const file = this.dataset.file;
//        console.log("cliccato un file");
//        openFileViewer(file);
//    });
//});

function openFileViewer(file) {
    fileViewer.innerHTML = `<img src="/r/${file}" alt="${file}" />`;
    fileViewer.style.display = 'block';
}

fileViewer.addEventListener('click', function(event) {
    if (event.target === this) {
        fileViewer.style.display = 'none';
    }
});
