 // Function to handle toggle switch state change
 document.getElementById('topicStatusToggle').addEventListener('change', function() {
    // Get the current URL without query params
    const currentUrl = window.location.origin + window.location.pathname;

    // Check if the toggle is checked (for 'closed' topics)
    const status = this.checked ? 'closed' : 'open';

    // Redirect to the new URL with the appropriate query string
    window.location.href = `${currentUrl}?status=${status}`;
});