function saveInputValues() {
    const fields = document.querySelectorAll('input[type="number"],input[type="text"], select');
    fields.forEach(field => {
        const { id, type, name, value } = field;
        if (id && type !== 'hidden' && name !== 'csrfmiddlewaretoken') {
            sessionStorage.setItem(id, value);
        }
    });
}

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

function triggerPageAtStart() {
  // if we've never been here in this tab…
  if (!sessionStorage.getItem('CO2Initialized')) {
    // 1) mark that we've initialized *before* any navigation happens
    sessionStorage.setItem('CO2Initialized', 'true');

    // 2) now do your save + click
    saveInputValues();
    document.getElementById('CO2button').click();
  }
}

// Event listener for DOMContentLoaded event
document.addEventListener('DOMContentLoaded', function() {
    triggerPageAtStart();
    // Load input values when the page is loaded
    loadInputValues();
   
    
    // Add change event listener to input fields to save input values and submit the form
    document.querySelectorAll('input, select').forEach(field => {
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