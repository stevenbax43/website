// Function to save input values to sessionStorage
function saveInputValues() {
    document.querySelectorAll('input').forEach(field => {
        console.log(`Saving ${field.id}: ${field.value}`); // Debugging statement
        sessionStorage.setItem(field.id, field.value);
    });
}

// Function to load input values from sessionStorage
function loadInputValues() {
    document.querySelectorAll('input').forEach(field => {
        const savedValue = sessionStorage.getItem(field.id);
        if (savedValue !== null) {
            field.value = savedValue;
            console.log(`Loaded ${field.id}: ${field.value}`);
        }
    });
}



// Event listener for DOMContentLoaded event
document.addEventListener('DOMContentLoaded', function() {
    // Load input values when the page is loaded
    loadInputValues();

   
    // Add change event listener to input fields to save input values and submit the form
    document.querySelectorAll('input').forEach(field => {
        field.addEventListener('change', function() {
            console.log(`Change event detected for ${field.id}`); // Debugging statement
            saveInputValues();

            // Submit the form when an input value changes
            const form = document.getElementById('inputForm');
            if (form) {
                console.log('Form found, submitting...'); // Debugging statement
                form.submit();
            } else {
                console.error('Form not found');
            }
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

    
    // Event listener for readme button
    document.getElementById('readMeButton').addEventListener('click', function() {
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