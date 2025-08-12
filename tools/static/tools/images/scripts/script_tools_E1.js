// JavaScript function to calculate pressure loss and related values
function calculateVermogen(U_spanning, I_stroom, Phi_factor) {
    
    // Function to calculate Reynolds number
    function actiefvermogen(U_spanning, I_stroom, Phi_factor) {
        return (U_spanning * I_stroom * Math.sqrt(3)*Phi_factor / 1000);
    }

    // Function to calculate Reynolds number
    function schijnbaarvermogen(U_spanning, I_stroom) {
        return (U_spanning * I_stroom * Math.sqrt(3) / 1000);
    }
   
    // Calculate values
    const P_actief = actiefvermogen(U_spanning, I_stroom, Phi_factor);
    const S_schijn = schijnbaarvermogen(U_spanning, I_stroom);
    const B_blind = Math.sqrt(S_schijn**2 - P_actief**2)

    // Create the result list
    const vermogenList = [
        P_actief.toFixed(2),
        S_schijn.toFixed(2),
        B_blind.toFixed(2),
    ];

    return vermogenList;
}

const sliders = [
    { id: 'U_spanning', valueId: 'slider-value1' },
    { id: 'I_stroom', valueId: 'slider-value2' },
    { id: 'Phi_factor', valueId: 'slider-value3' }
];

// Function to update the displayed values and perform calculation
function updateValues() {
    // Get values from sliders
    const U = parseFloat(document.getElementById('U_spanning').value);
    const I = parseFloat(document.getElementById('I_stroom').value);
    const CosPhi = parseFloat(document.getElementById('Phi_factor').value);

    // Calculate drukverlies
    const result = calculateVermogen(U, I, CosPhi);
    //console.log('Calculation result:', result);
    // Update result display
    document.getElementById('P_actief').textContent = ` ${Math.round(result[0])} `;
    document.getElementById('S_schijn').textContent = ` ${Math.round(result[1])}`;
    document.getElementById('B_blind').textContent = ` ${Math.round(result[2])}`;
    
    // Update arrow based on I_stroom
    drawArrows(Math.round(result[0]),Math.round(result[1]),Math.round(result[2]),CosPhi);
    //drawArrows(400,400,153,0.85);
}

// Function to draw the arrows
function drawArrows(P_actief, S_Schijn, B_blind,CosPhi) {
   
    const canvas = document.getElementById('arrowCanvas');
    const ctx = canvas.getContext('2d');
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);   // Clear the canvas

    //start drawing lines
    const lineWidth = 5
    const arrowLengthP = P_actief; // Map to 0-200px arrow length

    // Arrow properties
    const startX = 300; // Canvas center (x-coordinate)
    const startY = 50; // Canvas center (y-coordinate)

    // First arrow pointing to the right
    const endX1 = startX + arrowLengthP; // Arrow extends to the right by arrowLength
    const endY1 = startY; // Arrow remains at the same y-coordinate

    // Draw the first arrow shaft
    ctx.beginPath();
    offset = 10
    ctx.moveTo(startX, startY-5);
    ctx.lineTo(endX1, endY1-5);
    ctx.lineWidth = lineWidth;
    ctx.strokeStyle = 'blue';
    ctx.stroke();

    // Draw the first arrowhead
    const arrowheadSize = 10;
    ctx.beginPath();
    ctx.moveTo(endX1+5 - arrowheadSize, endY1 - 0.5*arrowheadSize-5);
    ctx.lineTo(endX1+5, endY1-5);
    ctx.lineTo(endX1+5 - arrowheadSize, endY1 + 0.5*arrowheadSize-5);
    ctx.fillStyle = 'blue';
    ctx.fill();

    // Label for the first arrow
    ctx.font = '14px Arial';
    ctx.fillStyle = 'blue';
    ctx.fillText(`Actief: ${P_actief} kW`, endX1 -90, endY1-15);

    // Second arrow with an angle
    const angleRadians = Math.acos(CosPhi) 
    const arrowLengthS = Math.round(S_Schijn)//between 0 and 90 degrees. 
    
    const endY2 = startY + arrowLengthS * Math.sin(angleRadians); // Adjust y-coordinate by angle

    // Draw the second arrow shaft
    ctx.beginPath();
    ctx.moveTo(startX , startY);
    ctx.lineTo(endX1, endY2 );
    ctx.lineWidth = lineWidth;
    ctx.strokeStyle = 'red';
    ctx.stroke();

    //Debug
    DeltaS = 5
    XdeltaS = endX1+DeltaS*Math.cos(angleRadians)
    YdeltaS = endY2+DeltaS * Math.sin(angleRadians)
    test = Math.cos(Math.PI/6)*180/Math.PI
    console.log(test)
    const baseLeftX = XdeltaS - arrowheadSize * Math.cos(angleRadians + Math.PI / 6);
    const baseLeftY = YdeltaS - arrowheadSize * Math.sin(angleRadians + Math.PI / 6);

    const baseRightX = XdeltaS - arrowheadSize * Math.cos(angleRadians - Math.PI / 6);
    const baseRightY = YdeltaS - arrowheadSize * Math.sin(angleRadians - Math.PI / 6);

    // Draw the second arrowhead
    ctx.beginPath();
    ctx.moveTo(baseLeftX, baseLeftY); // Left base point
    ctx.lineTo(XdeltaS, YdeltaS);        // Arrow tip
    ctx.lineTo(baseRightX, baseRightY); // Right base point
    ctx.closePath();
    ctx.fillStyle = 'red';
    ctx.fill();

    // Label for the second arrow
    ctx.font = '14px Arial';
    ctx.fillStyle = 'red';
    ctx.fillText(`Schijnbaar: ${arrowLengthS} kVA`, endX1 - 140, endY2+20);

    // Draw the third arrow shaft
    ctx.beginPath();
    ctx.moveTo(endX1 + offset, startY);
    ctx.lineTo(endX1 + offset, endY2);
    ctx.lineWidth = lineWidth;
    ctx.strokeStyle = 'orange';
    ctx.stroke();

    // Draw the third arrowhead
    ctx.beginPath();
    ctx.moveTo(endX1 - 0.5*arrowheadSize + offset, endY2 +5- arrowheadSize);// Move to the left side of the arrow (the start of the arrowhead)
    ctx.lineTo(endX1+offset, endY2+5); // Draw the main line from the base of the arrowhead to the tip
    ctx.lineTo(endX1 + 0.5*arrowheadSize+offset, endY2 +5 - arrowheadSize);// Draw the right side of the arrowhead
    ctx.fillStyle = 'orange';
    ctx.fill();

    // Label for the third arrow
    ctx.font = '14px Arial';
    ctx.fillStyle = 'orange';
    ctx.fillText(`Blind: ${B_blind} kVA`, endX1 +20, endY2-10);
}


// Function to synchronize slider and input field
function syncSliderAndInput(sliderId, inputId) {
    const slider = document.getElementById(sliderId);
    const input = document.getElementById(inputId);

    function updateInputFromSlider() {
        input.value = slider.value;
    }

    function updateSliderFromInput() {
        const newValue = parseFloat(input.value);
        if (!isNaN(newValue)) {
            slider.value = Math.max(slider.min, Math.min(slider.max, newValue));
            input.value = slider.value;
        }
    }
    slider.addEventListener('input', updateInputFromSlider);
    input.addEventListener('input', updateSliderFromInput);

    updateInputFromSlider();
}
// Event listener for DOMContentLoaded event
document.addEventListener('DOMContentLoaded', function() {
    // Initialize sliders and text inputs
    syncSliderAndInput('U_spanning', 'slider-value1');
    syncSliderAndInput('I_stroom', 'slider-value2');
    syncSliderAndInput('Phi_factor', 'slider-value3');

    // Auto-submit on slider change
    document.querySelectorAll('input[type="range"], input[type="number"]').forEach(slider => {
        slider.addEventListener('input', updateValues);
    });

    // Initialize values on page load
    updateValues();

    // Event listener for print button
    document.getElementById('printButton').addEventListener('click', function() {
        window.print();
    });

    // Event listener for readme button
    document.getElementById('readMeButton').addEventListener('click', function() {
        window.open(pdfUrlReadMe, '_blank');
    });

    // Event listener for excel button
    document.getElementById('excelButton').addEventListener('click', function() {
        window.open(pdfUrlExcel, '_blank');
    });
});
