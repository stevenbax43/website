document.addEventListener("DOMContentLoaded", function() {
    // Get all elements with the class "first-letters"
    var usernameContainers = document.querySelectorAll(".first-letters");

    // Loop through each element for user first letters
    usernameContainers.forEach(function (usernameContainer) {
        // Extract the first two letters
        var firstTwoLetters = usernameContainer.textContent.trim().slice(0, 2);

        // Update the content of the element
        usernameContainer.innerHTML = firstTwoLetters;
    });
    CKEDITOR.replace('id_content', {
        removePlugins: 'easyimage, cloudservices',
        ignoreEmptyParagraph: true,
        removeButtons: '',
        disableNativeSpellChecker: false,
        height: 300,
        width:1000,
        removePlugins: 'scayt',
        ignoreSecurityWarnings: true
    });
});
