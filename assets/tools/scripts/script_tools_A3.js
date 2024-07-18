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
function updateMaxValue() {
    var HeatPowerMax = document.getElementById("HeatPowerMax");
    var maxPowerHeat = document.getElementById("maxPowerHeat");
    var CoolPowerMax = document.getElementById("CoolPowerMax");
    var maxPowerCool = document.getElementById("maxPowerCool");
    var minPowerHeat = document.getElementById("minPowerHeat");
    var minPowerCool = document.getElementById("minPowerCool");

    maxPowerHeat.max = HeatPowerMax.value; // maximale waarde bovengrens is max vermogen verwarmen
    maxPowerCool.max = CoolPowerMax.value; // maximale waarde bovengrens is max vermogen koelen
    minPowerHeat.max = maxPowerHeat.value; // maximale waarde ondergrens is bovengrens verwamen
    minPowerCool.max = maxPowerCool.value; // maximale waarde ondergrens is bovengrens verwamen
}


// Event listener for DOMContentLoaded event
document.addEventListener('DOMContentLoaded', function() {
    // Load input values when the page is loaded
    loadInputValues();
    updateMaxValue(); 

    // Add change event listener to input fields to save input values and simulate click on the submit button
    document.querySelectorAll('input, select').forEach(field => {
        field.addEventListener('change', function() {
            saveInputValues();
            if (field.id === 'HeatPowerMax' || field.id==='CoolPowerMax') {
                updateMaxValue();
            }
            document.getElementById('bedrijfsurenknop').click();
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
        
        fetch(downloadExcelUrl)
            
            .then(response => response.blob())
            .then(blob => {
                // Create a temporary URL for the blob
                const url = window.URL.createObjectURL(blob);

                // Create a download link
                const link = document.createElement('a');
                link.href = url;
                link.download = 'Klimaatjaar_2018.xlsx';

                // Simulate a click event on the download link
                link.click();

                // Cleanup: remove the temporary URL
                window.URL.revokeObjectURL(url);
            });
    });
   
});