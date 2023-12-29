//show a wainting sign after button pressed
document.addEventListener('DOMContentLoaded', () => {
    const waitingSign = document.getElementById('waitingSign');
    const EPButton = document.getElementById('EP_button');
    

    EPButton.addEventListener('click', () => {
        // Show the waiting sign by removing the 'hidden' class
        waitingSign.classList.remove('hidden');

        // Set a timeout to remove the waiting sign after 5 seconds
        setTimeout(() => {
            // Hide the waiting sign by adding the 'hidden' class
            waitingSign.classList.add('hidden');
        }, 12000); // 12000 milliseconds = 12 seconds
    });
});

//PDF creater
document.getElementById('PDF_creater').addEventListener('click', function() {
    const pText = document.querySelector('p');
    const longtext = documentm.getElementById(''); 
    console.log(pText.innerText);
    // Create a jsPDF instance
    const pdf = new jsPDF();
  
    // Add content to the PDF
    pdf.text(pText.innerText, 10, 10);
    pdf.text("This is title 2", 10, 20);
  
    // Save the PDF
    pdf.save('simple.pdf');
  });
