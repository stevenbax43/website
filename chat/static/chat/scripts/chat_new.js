document.addEventListener('DOMContentLoaded', () => {
    
    function sendMessage() {
        // Get elements
        const userInputElement = document.getElementById('user_input_first');
        const chatDisplay = document.getElementById('chat-display');
        const usernameElement = document.getElementById('current_username'); // Ensure this element exists in your HTML
        
        // Check if elements are present
        if (!userInputElement || !chatDisplay || !usernameElement) {
            console.error('Required elements are missing from the DOM.');
            return;
        }
      
        // Get values
        const userInput = userInputElement.value.trim();
        const username = usernameElement.textContent || usernameElement.innerHTML;
        const usernameInitials = username.length >= 2 ? username.slice(0, 2).toUpperCase() : username.toUpperCase();

        if (userInput === '') {
            console.error('No input');
            return; // Do not send if input is empty
        }
        
        // Add message to chat display
        chatDisplay.innerHTML += `
            <div class="message mb-2 user-message">
                <div class="user_chat wrap"><b>You</b> <br>${userInput}</div>
                <div class="circle_user first-letters">${usernameInitials}</div>
            </div>
        `;
        chatDisplay.scrollTop = chatDisplay.scrollHeight;

        // Send data to server
        fetch('/process-input/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value // Get CSRF token from the form
            },
            body: JSON.stringify({ input: userInput })
        })
        .then(response => response.json())
        .then(data => {
            if (data.redirect_url) {
                window.location.href = data.redirect_url;  // Redirect to the new chat page
            } else {
                console.error('Error:', data.error || 'Unknown error occurred');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });

        // Clear the input field
        userInputElement.value = '';
    }

    function handleEnterKey(event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent form submission
            sendMessage(); // Call the sendMessage function
        }
    }

    // Attach event listeners
    const userInputElement = document.getElementById('user_input_first');
    const sendButton = document.getElementById('sent_input');

    if (userInputElement) {
        userInputElement.addEventListener('keydown', handleEnterKey);
    }

    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }
});