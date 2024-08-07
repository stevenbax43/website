// JavaScript function to calculate pressure loss and related values
function calculateDrukverlies(di_value, velocity, length) {
    // Constants
    const kinematicViscosity = 1.0084e-6; // Pa·s (e.g., water at room temperature)
    const roughness = 4.5e-6; // meters (e.g., pipe roughness)
    const density = 997.3; // kg/m³ (e.g., water)

    // Data dictionary
    const dataDict = {
        15: { "Du": 21.3, "δbuis": 2.6, "Di": 16.1 },
        20: { "Du": 26.9, "δbuis": 2.6, "Di": 21.7 },
        25: { "Du": 33.7, "δbuis": 3.2, "Di": 27.3 },
        32: { "Du": 42.4, "δbuis": 3.2, "Di": 36.0 },
        40: { "Du": 48.3, "δbuis": 3.2, "Di": 41.9 },
        50: { "Du": 60.3, "δbuis": 3.6, "Di": 53.1 },
        65: { "Du": 76.1, "δbuis": 3.6, "Di": 68.9 },
        80: { "Du": 88.9, "δbuis": 4.0, "Di": 80.9 },
        100: { "Du": 114.3, "δbuis": 4.5, "Di": 105.3 }
    };

    // Function to get Di by DN value
    function getDiByDn(dnValue) {
        return dataDict[dnValue] ? dataDict[dnValue]["Di"] : "DN value not found";
    }

    // Function to calculate Reynolds number
    function reynoldsNumberKinematic(velocity, diValue, kinematicViscosity) {
        return (velocity * diValue / 1000) / kinematicViscosity;
    }

    // Function to calculate flow rate (m³/h)
    function debiet(velocity, diValue) {
        return (velocity * Math.pow((diValue / 1000),2)*Math.PI/4) * 3600;
    }

    // Function to calculate friction factor
    function frictionFactor(roughness, diValue, reynoldsNumber) {
        const term1 = roughness / (3.72 * diValue / 1000);
        const term2 = 5.74 / Math.pow(reynoldsNumber, 0.901);
        const inverseSqrtLambda = -2 * Math.log10(term1 + term2);
        return 1 / Math.pow(inverseSqrtLambda, 2);
    }

    // Function to calculate pressure loss (kPa)
    function pressureLoss(lambda, length, di_value, density, velocity) {
        return (lambda * (length / (di_value / 1000)) * 0.5 * density * Math.pow(velocity, 2))/1000;
    }

    // Calculate values
    const reynoldsNumber = reynoldsNumberKinematic(velocity, di_value, kinematicViscosity);
    const lambda = frictionFactor(roughness, di_value, reynoldsNumber);
    const pressureLossValue = pressureLoss(lambda, length, di_value, density, velocity);
    const flowM3H = debiet(velocity, di_value);
    const flowLS = flowM3H / 3.6;
    const flowLMin = flowLS * 60;

    // Create the result list
    const drukverliesList = [
        pressureLossValue,
        flowM3H.toFixed(2),
        flowLMin.toFixed(2),
        flowLS.toFixed(2)
    ];

    return drukverliesList;
}

const sliders = [
    { id: 'di_value', valueId: 'slider-value1' },
    { id: 'velocity', valueId: 'slider-value2' },
    { id: 'length', valueId: 'slider-value3' }
];

// Function to update the displayed values and perform calculation
function updateValues() {
    // Get values from sliders
    const diValue = parseFloat(document.getElementById('di_value').value);
    const velocity = parseFloat(document.getElementById('velocity').value);
    const length = parseFloat(document.getElementById('length').value);

    // Calculate drukverlies
    const result = calculateDrukverlies(diValue, velocity, length);
    console.log('Calculation result:', result);
    // Update result display
    document.getElementById('pressureLossBar').textContent = ` ${(result[0]/100).toFixed(2)} `;
    document.getElementById('pressureLosskPa').textContent = ` ${Math.round(result[0])} `;
    document.getElementById('flowM3H').textContent = ` ${result[1]}`;
    document.getElementById('flowLMin').textContent = ` ${result[2]}`;
    document.getElementById('flowLS').textContent = ` ${result[3]}`;
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
    syncSliderAndInput('length', 'slider-value3');
    syncSliderAndInput('velocity', 'slider-value2');
    syncSliderAndInput('di_value', 'slider-value1');
    
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

document.addEventListener('DOMContentLoaded', function() {
    const slider = document.getElementById('length');
    const textInput = document.getElementById('slider-value3');

    // Function to update the text input based on slider value
    function updateTextInputFromSlider() {
        textInput.value = slider.value;
    }

    // Function to update the slider based on text input value
    function updateSliderFromTextInput() {
        const newValue = parseFloat(textInput.value);
        if (!isNaN(newValue)) {
            // Ensure the value is within the slider's range
            slider.value = Math.max(slider.min, Math.min(slider.max, newValue));
            // Update the text input to match the slider value
            textInput.value = slider.value;
        }
    }

    // Event listener for slider input
    slider.addEventListener('input', updateTextInputFromSlider);

    // Event listener for text input change
    textInput.addEventListener('input', updateSliderFromTextInput);

    // Initialize the text input with the slider's value on page load
    updateTextInputFromSlider();
});