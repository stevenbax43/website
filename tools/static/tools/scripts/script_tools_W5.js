//https://flamco.aalberts-hfc.com/media/files/calculationtools/ins.vls.flexcon-calculation-page_1.pdf
// Function to save input values to sessionStorage
// Function to save input values into sessionStorage
function saveInputValues() {
    const fields = document.querySelectorAll('input[type="number"],input[type="text"], select');
    fields.forEach(field => {
        const { id, type, name, value } = field;
        if (id && type !== 'hidden' && name !== 'csrfmiddlewaretoken') {
            sessionStorage.setItem(id, value);
        }
    });
}

// Function to load input values from sessionStorage
function loadInputValues() {
    const fields = document.querySelectorAll('input[type="number"],input[type="text"], select');
    fields.forEach(field => {
        const { id, type, name } = field;
        if (id && type !== 'hidden' && name !== 'csrfmiddlewaretoken') {
            const savedValue = sessionStorage.getItem(id);
            if (savedValue !== null) {
                field.value = savedValue;
            }
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
            document.getElementById('calculateButton').click();
        });
    });

    // Add change event listener to input fields to save input values dynamically
    document.querySelectorAll('input, select').forEach(field => {
        field.addEventListener('change', saveInputValues);
    });


    // Event listener for print button
    document.getElementById('printButton').addEventListener('click', function() {
        window.print();
    });

    // Placeholder for readme button functionality
    document.getElementById('readMeButton').addEventListener('click', function() {
    //     // Handle Excel button click event
        window.open(pdfUrlReadMe, '_blank');
    });
    // Event listener for excel button
    document.getElementById('excelButton').addEventListener('click', function() {
        // Make a GET request to the Django view that generates the Excel file
        window.open(pdfUrlExcel, '_blank');
    });
});

