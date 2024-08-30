document.addEventListener('DOMContentLoaded', () => {
    // Define sendMessage function in the global scope
    window.sendMessage = function() {
        var userInput = document.getElementById('user_input').value.trim();
        const conversationIdElement  = document.getElementById('conversation-id')
        var username = document.getElementById('current_username').textContent || document.getElementById('current_username').innerHTML;
        document.getElementById('user_input').value = '';

        if (!userInput) return; // Prevent sending empty messages

        // Get first two letters of username
        username = username.substring(0, 2).toUpperCase();
        var chatDisplay = document.getElementById('chat-display');
        chatDisplay.innerHTML += `
            <div class="message mb-2 user-message">
                <div class="user_chat wrap"><b>You</b> <br>${userInput}</div>
                <div class="circle_user first-letters">${username}</div>
            </div>
        `;
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
        // Fetch the conversation ID (pk) if available
        var conversationId = conversationIdElement ? conversationIdElement.value : null;
    
        // Construct the POST body with user_input and conversation_id (if available)
        const postData = `user_input=${encodeURIComponent(userInput)}`;

        var postUrl = conversationId ? `/chatbot/${conversationId}/` : '/chatbot/';

        console.log(`POST URL: ${postUrl}`);
        console.log(`POST Data: ${postData}`);
            // Send the user input to the server and get the response
        fetch(postUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: postData
        })
        .then(response => response.json())
            
        .then(data => {
            chatDisplay.innerHTML += `
                <div class="message mb-2 bot-message">
                    <div class="circle_bot">K</div>
                    <div class="bot_response wrap"><b>Chatbot</b> <br>${data.response}</div>
                </div>
            `;
            chatDisplay.scrollTop = chatDisplay.scrollHeight;
        })
        .catch(error => console.error('Error:', error));
    };
    
    // Handle Enter key press
    window.handleEnterKey = function(event) {
        console.log("handleEnterKey called");
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    };

    // Get CSRF token from cookies
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
