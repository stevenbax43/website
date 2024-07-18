// Function to save input values to sessionStorage
function saveInputValues() {
    document.querySelectorAll('input, select').forEach(field => {
        sessionStorage.setItem(field.id, field.value);
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
    // Load input values when the page is loaded
    loadInputValues();

    // Add change event listener to input fields to save input values and simulate click on the submit button
    document.querySelectorAll('input, select').forEach(field => {
        field.addEventListener('change', function() {
            saveInputValues();
            document.getElementById('mollierButton').click();
        });
    });

    // Remember and restore scroll position
    const scrollPosition = sessionStorage.getItem('scrollPosition');
    if (scrollPosition) {
        window.scrollTo(0, parseInt(scrollPosition));
    }

    window.addEventListener('scroll', function() {
        sessionStorage.setItem('scrollPosition', window.scrollY);
    });

    // Event listener for buttons with class 'save-and-reload' to save input values and reload the page
    document.querySelectorAll('.save-and-reload').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent form submission
            saveInputValues(); // Save input values to sessionStorage
            location.reload(); // Reload the page
        });
    });
    // Placeholder for readme button functionality
    document.getElementById('readMeButton').addEventListener('click', function() {
        //     // Handle Excel button click event
            window.open(pdfUrlReadMe, '_blank');
    });
    // Event listener for print button
    document.getElementById('printButton').addEventListener('click', function() {
        window.print();
    });

    // Event listener for excel button
    document.getElementById('excelButton').addEventListener('click', function() {
        // Make a GET request to the Django view that generates the Excel file
        window.open(pdfUrlExcel, '_blank');
    });
});