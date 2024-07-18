//https://flamco.aalberts-hfc.com/media/files/calculationtools/ins.vls.flexcon-calculation-page_1.pdf
// Function to save input values to sessionStorage
// Function to save input values into sessionStorage
function saveInputValues() {
    document.querySelectorAll('input, select').forEach(field => {
        sessionStorage.setItem(field.id, field.value);
    });
    const locatieToggle = document.getElementById('locatieToggle').checked;
    sessionStorage.setItem('locatieToggle', locatieToggle);
}

// Function to load input values from sessionStorage
function loadInputValues() {
    document.querySelectorAll('input, select').forEach(field => {
        const savedValue = sessionStorage.getItem(field.id);
        if (savedValue !== null) {
            field.value = savedValue;
        }
    });
    const locatieToggle = sessionStorage.getItem('locatieToggle') === 'true';
    document.getElementById('locatieToggle').checked = locatieToggle;
}

// Function to toggle additional fields visibility and store state in sessionStorage
function toggleAdditionalFields(isExpanded) {
    const additionalFields = document.getElementById('additional_fields');
    const toggleButton = document.getElementById('toggleButton');
    const icon = toggleButton.querySelector('i');

    if (additionalFields) {
        if (isExpanded) {
            additionalFields.classList.add('show');
        } else {
            additionalFields.classList.remove('show');
        }
    }

    // Update toggle button aria-expanded attribute, icon, and text
    toggleButton.setAttribute('aria-expanded', isExpanded);
    icon.classList.toggle('fa-chevron-down', !isExpanded);
    icon.classList.toggle('fa-chevron-up', isExpanded);
    toggleButton.innerHTML = `<i class="fas ${isExpanded ? 'fa-chevron-up' : 'fa-chevron-down'}"></i> ${isExpanded ? 'Inklappen' : 'Uitbreiden'}`;

    // Store state in sessionStorage
    sessionStorage.setItem('additionalFieldsExpanded', isExpanded);
}

// Event listener for DOMContentLoaded event
document.addEventListener('DOMContentLoaded', function() {
    // Load input values when the page is loaded
    loadInputValues();
   
    // Load additional fields toggle state from sessionStorage
    const storedState = sessionStorage.getItem('additionalFieldsExpanded');
    const isExpanded = storedState === 'true'; // Convert string to boolean

    // Initial toggle based on sessionStorage or default
    toggleAdditionalFields(isExpanded);

    // Event listener for toggle button click
    const toggleButton = document.getElementById('toggleButton');
    toggleButton.addEventListener('click', function() {
        const isCurrentlyExpanded = toggleButton.getAttribute('aria-expanded') === 'true';
        const newExpandedState = !isCurrentlyExpanded;
        toggleAdditionalFields(newExpandedState);
    });

    // Event listener for form submission
    
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

