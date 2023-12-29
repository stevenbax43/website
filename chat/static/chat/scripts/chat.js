function handleEnterKey(event) {
    console.log("handleEnterKey called");
    // Check if the Enter key (key code 13) is pressed
    if (event.key === "Enter") {
        // Prevent the default form submission behavior
        event.preventDefault();
        // Call the function to handle sending the message
        sendMessage();
    }
}

function sendMessage() {
    console.log("sendMessage called");
    var userInput = document.getElementById('user-input').value;
    var username = document.getElementById('current_username').textContent || document.getElementById('current_username').innerHTML ;
    document.getElementById('user-input').value = '';

    //get first two letters of username
    username = username.substring(0, 2).toUpperCase();
    var chatDisplay = document.getElementById('chat-display');
    chatDisplay.innerHTML += '<div class="message"><div class="circle_user">'+ username +'</div><div class="user_chat"><b>You</b> <br>' + userInput + '</div></div>'

    // Send the user input to the server and get the response
    fetch('/chatbot/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: 'user_input=' + encodeURIComponent(userInput),
    })
    .then(response => response.json())
    .then(data => {
        var chatDisplay = document.getElementById('chat-display');
        chatDisplay.innerHTML += '<div class="message"><div class="circle_bot">'+ 'K' +'</div><div class="user_bot"><b>Chat</b> <br>' + data.response + '</div></div>'
    })
    .catch(error => console.error('Error:', error));
}
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Check if this cookie string begins with the name we want
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


 // Get all elements with the class "first-letters"
var usernameContainers = document.querySelectorAll(".first-letters");

// Loop through each element
usernameContainers.forEach(function (usernameContainer) {
    // Extract the first two letters
    var firstTwoLetters = usernameContainer.textContent.slice(0, 2);

    // Update the content of the element
    usernameContainer.innerHTML = firstTwoLetters;
});