// Function to save input values to sessionStorage
// Function to save input values into sessionStorage
function saveInputValues() {
    document.querySelectorAll('input, select').forEach(field => {
        if(field.type !== 'hidden' && field.name !== 'csrfmiddlewaretoken'){ // ensure the CSRF-token is not saved in the session-storage. 
            sessionStorage.setItem(field.id, field.value);
        }
    });
    
}

// Function to load input values from sessionStorage
function loadInputValues() {
    document.querySelectorAll('input, select').forEach(field => {
        const savedValue = sessionStorage.getItem(field.id);
        if (savedValue !== null) {
            field.value = savedValue;
        }
    });
}

// Event listener for DOMContentLoaded event
document.addEventListener('DOMContentLoaded', function() {
    let pcodeChanged = false;
    let hnumberChanged = false;

    // Function to check if both fields have changed
    function checkBothChanged() {
        if (pcodeChanged && hnumberChanged) {
            document.getElementById('searchButton').click();
        }
    }

    // Add change event listener to pcode input field
    document.getElementById('pcode').addEventListener('change', function() {
        pcodeChanged = true;
        saveInputValues(); // Save input values when pcode changes
        checkBothChanged(); // Check if both fields have changed
    });

    // Add change event listener to hnumber input field
    document.getElementById('hnumber').addEventListener('change', function() {
        hnumberChanged = true;
        saveInputValues(); // Save input values when hnumber changes
        checkBothChanged(); // Check if both fields have changed
    });

    // Add change event listener to other input fields to save input values dynamically
    document.querySelectorAll('input:not(#pcode, #hnumber), select').forEach(field => {
        field.addEventListener('change', saveInputValues);
    });

    // Load input values when the page is loaded
    loadInputValues();

    // Event listener for print button
    document.getElementById('printButton').addEventListener('click', function() {
        window.print();
    });

    // Placeholder for readme button functionality
    document.getElementById('readMeButton').addEventListener('click', function() {
    //     // Handle Excel button click event
        window.open(pdfUrlReadMe, '_blank');
    });
});

