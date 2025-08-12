
// Event listener for DOMContentLoaded event
document.addEventListener('DOMContentLoaded', function() {
    // Event listener for print button
   
    document.getElementById('printButton').addEventListener('click', function() {
        window.print();
    });
    // Event listener for excel button
    document.getElementById('excelButton').addEventListener('click', function() {
        // Make a GET request to the Django view that generates the Excel file
        window.open(pdfUrlExcel, '_blank');
    });
})