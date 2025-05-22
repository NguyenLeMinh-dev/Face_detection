function toggleDetection() {
    fetch('/toggle', { method: 'POST' })
        .then(() => {
            alert("Toggled Face Detection!");
        });
}
