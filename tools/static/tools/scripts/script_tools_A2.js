//https://www.eenheden.com/debiet-m3-h-s-cfm-cfs-gpm.php
// Conversion table
var conversion_table = {
    Afstand: { meter: 1, millimeter: 1000, centimeter: 100, decimeter: 10, kilometer: 0.001, feet: 3.28084, inches: 39.3701, seamile: 0.000539957, landmile: 0.000621371 },
    Massa: { kilogram: 1, gram: 1000, milligram: 1000000, ton: 0.001, pond: 2.20462 },
    Druk: { pascal: 1, kilopascal: 0.001, mH2O: 0.00010204081632, bar: 0.000010204081632, millibar: 0.010204081632},
    Volume: { cubicmeters: 1, liters: 1000, milliliters: 1000000, gallons:264.17},
    Debiet: { cubicmeterpersecond: 1, cubicmeterperhour: 3600, cubicmeterperminute: 60, litersperhour: 3600000, litersperminute: 60000, literspersecond: 1000,cubicfeetperminute:2118.88},
    Energie: { joules: 1, kilojoules: 0.001, kilowattuur: 0.0000002778, wattuur: 0.0002778, wattseconde: 1, britischthermalunits: 0.0009478, calorie: 0.2388, kilocalorie: 0.0002388},
    
};

function convert() {
    var targetDiv = document.querySelector(".maintoola2[style='display: flex;']");

    if (!targetDiv) {
        alert("No category selected!");
        return;
    }

    var value = parseFloat(targetDiv.querySelector("#value").value);
    var fromUnit = targetDiv.querySelector("#from").value;
    var toUnit = targetDiv.querySelector("#to").value;
    var magnitude = targetDiv.querySelector("#magnitude").innerHTML;
    
    // Check if conversion is possible
    if (!conversion_table.hasOwnProperty(magnitude)) {
        alert("Invalid category: " + magnitude);
        return;
    }

    if (!conversion_table[magnitude].hasOwnProperty(fromUnit) || !conversion_table[magnitude].hasOwnProperty(toUnit)) {
        alert("Conversion from " + fromUnit + " to " + toUnit + " is not supported in category " + magnitude);
        return;
    }

    // Perform conversion
    var fromUnitToBase = conversion_table[magnitude][fromUnit];
    var toUnitToBase = conversion_table[magnitude][toUnit];
    var conversionFactor = toUnitToBase / fromUnitToBase;
    var result = (value * conversionFactor);

    // Display result in the corresponding output container
    var outputContainer = targetDiv.querySelector(".output-container output");
    if (outputContainer) {
        outputContainer.innerHTML = result;
    } else {
        alert("Output container not found!");
    }
}


// Add event listener for click event
document.getElementById("categoryList").addEventListener("click", function(event) {
  // Check if the clicked element is an li
  if (event.target.tagName === "LI") {
    var targetDivId = event.target.getAttribute("data-target");

    // Hide all divs with class "maintoola2"
    var allDivs = document.querySelectorAll(".maintoola2");
    allDivs.forEach(function(div) {
      div.style.display = "none";
    });

    // Show the corresponding div
    var targetDiv = document.getElementById(targetDivId);
    if (targetDiv) {
      targetDiv.style.display = "flex";
      //convert();
    }
  }
});


// Attach event listeners to input field and select elements within the maintoola2 divs
var maintoola2Divs = document.querySelectorAll('.maintoola2');
maintoola2Divs.forEach(function(div) {
    div.querySelector('#value').addEventListener('input', convert);
    div.querySelector('#from').addEventListener('change', convert);
    div.querySelector('#to').addEventListener('change', convert);
});
// Event listener for DOMContentLoaded event
document.addEventListener('DOMContentLoaded', function() {
  // Event listener for print button
  document.getElementById('readMeButton').addEventListener('click', function() {
      window.open(pdfUrlReadMe, '_blank');
  });
  document.getElementById('printButton').addEventListener('click', function() {
      window.print();
  });
  // Event listener for excel button
  document.getElementById('excelButton').addEventListener('click', function() {
      // Make a GET request to the Django view that generates the Excel file
      window.open(pdfUrlExcel, '_blank');
  });
})