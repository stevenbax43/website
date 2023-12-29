//https://www.eenheden.com/debiet-m3-h-s-cfm-cfs-gpm.php

function convert() {
    // Get values from inputs
    var value = parseFloat(document.getElementById('value').value);
    var fromUnit = document.getElementById('from').value;
    var toUnit = document.getElementById('to').value;

    // Perform the conversion
    var result;
    switch (fromUnit) {
         //Druk ------------------------------------------------------------------------
        case 'kilopascal':
            result = convertFromKiloPascal(value, toUnit);
            break;
        case 'mH2O':
            result = convertFrommH20(value, toUnit);
            break;
        case 'pascal':
            result = convertFromPascal(value, toUnit);
            break;
        case 'bar':
            result = convertFromBar(value, toUnit);
        case 'millibar':
                result = convertFromMilliBar(value, toUnit);
            break;
        //Volume -----------------------------------------------------------------------
        case 'milliliters':
            result = convertFromMilliliters(value, toUnit);
            break;
        case 'liters':
            result = convertFromLiters(value, toUnit);
            break;
        case 'cubicmeters':
            result = convertFromCubicMeters(value, toUnit);
            break;
        //Debiet -----------------------------------------------------------------------
        case 'cubicmeterperhour':
            result = convertFromCubicMeterPerHour(value, toUnit);
            break;
        case 'cubicmeterperminute':
            result = convertFromCubicMeterPerMinute(value, toUnit);
            break;
        case 'cubicmeterpersecond':
            result = convertFromCubicMeterPerSecond(value, toUnit);
            break;
        case 'litersperhour':
            result = convertFromLiterPerHour(value, toUnit);
            break;
        case 'litersperminute':
            result = convertFromLiterPerMinute(value, toUnit);
            break;
        case 'literspersecond':
            result = convertFromLiterPerSecond(value, toUnit);
            break;
        //Massa -----------------------------------------------------------------------
        case 'kilogram':
            result = convertFromKiloGram(value, toUnit);
            break;
        case 'gram':
            result = convertFromGram(value, toUnit);
            break;
        case 'milligram':
            result = convertFromMilliGram(value, toUnit);
            break;
        case 'ton':
            result = convertFromTon(value, toUnit);
            break;
        case 'pond':
            result = convertFromPond(value, toUnit);
            break;
        //Energie -----------------------------------------------------------------------
        case 'joules':
            result = convertFromJoules(value, toUnit);
            break;
        case 'kilojoules':
            result = convertFromKiloJoules(value, toUnit);
            break;
        case 'kilowattuur':
            result = convertFromKiloWattUur(value, toUnit);
            break;
        case 'wattuur':
            result = convertFromWattUur(value, toUnit);
            break;
        case 'wattseconde':
            result = convertFromWattSeconde(value, toUnit);
            break;
        case 'britishthermalunit':
            result = convertFromBritishThermalUnit(value, toUnit);
            break;
        case 'calorie':
            result = convertFromCalorie(value, toUnit);
            break;
        case 'kilocalorie':
            result = convertFromKiloCalorie(value, toUnit);
            break;


        // Add more cases for other units as needed
        default:
            result = 'Invalid unit';
    }

    // Display the result
    document.getElementById('result').innerText = result;
}
//--------------------------------------------------------------------------------------------------
// function "Druk"
function convertFromKiloPascal(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'kilopascal':
            return value * 1; //
        case 'pascal':
            return value * 1000; // 
        case 'mH2O':
            return value * 0.102 ; // 
        case 'bar':
            return value * 0.0102; // 
        case 'millibar':
            return value * 10.2; //
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
function convertFromPascal(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'kilopascal':
            return value / 1000; //
        case 'pascal':
            return value * 1; // 
        case 'mH2O':
            return value * 0.000102 ; // 
        case 'bar':
            return value * 0.00001; // 
        case 'millibar':
            return value * 0.01; //
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
function convertFrommH2O(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'kilopascal':
            return value * 9.8; //
        case 'pascal':
            return value * 9800; // 
        case 'mH2O':
            return value * 1 ; // 
        case 'bar':
            return value * 0.1; // 
        case 'millibar':
            return value * 100; //
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
function convertFromBar(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'kilopascal':
            return value * 98; //
        case 'pascal':
            return value * 9800; // 
        case 'mH2O':
            return value * 10  ; // 
        case 'bar':
            return value * 1; // 
        case 'millibar':
            return value * 1000; //
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
function convertFromMilliBar(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'kilopascal':
            return value * 98 / 1000; //
        case 'pascal':
            return value * 9800 / 1000; // 
        case 'mH2O':
            return value * 10 / 1000  ; // 
        case 'bar':
            return value / 1000; // 
        case 'millibar':
            return value * 1; //
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
//--------------------------------------------------------------------------------------------------------
// functions "Volume"
function convertFromMilliliters(value, toUnit) {
    // Implement the conversion logic for milliliters
    // Return the converted value
    switch (toUnit) {
        case 'milliliters':
            return value; // 1 liter = 1000 milliliters
        case 'liters':
            return value / 1000; // 1 liter = 1000 milliliters
        case 'cubicmeters':
            return value / 1000000; // 1 liter = 1000000 cubicmeters
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
function convertFromLiters(value, toUnit) {
    // Implement the conversion logic for liters
    // Return the converted value
    switch (toUnit) {
        case 'milliliters':
            return value * 1000; // 1 liter = 1000 milliliters
        case 'liters':
            return value; // 1 liter = 1000 milliliters
        case 'cubicmeters':
            return value / 1000; // 1 liter = 1000000 cubicmeters
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
function convertFromCubicMeters(value, toUnit) {
    // Implement the conversion logic for liters
    // Return the converted value
    switch (toUnit) {
        case 'milliliters':
            return value * 1000000; // 1 liter = 1000 milliliters
        case 'liters':
            return value * 1000; // 1 liter = 1000 milliliters
        case 'cubicmeters':
            return value ; // 1 liter = 1000000 cubicmeters
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}

//--------------------------------------------------------------------------------------------------------
// functions "Debiet"
function convertFromCubicMeterPerHour(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'cubicmeterperhour':
            return value * 1; // 
        case 'cubicmeterperminute':
            return value / 60; // 
        case 'cubicmeterpersecond':
            return value  / 3600 ; // 60*60 = 3600
        case 'litersperhour':
            return value * 1000; //
        case 'litersperminute':
            return value * 1000 /60; // 
        case 'literspersecond':
            return value * 1000/3600; // 
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
function convertFromCubicMeterPerMinute(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'cubicmeterperhour':
            return value * 60; // 
        case 'cubicmeterperminute':
            return value * 1; // 
        case 'cubicmeterpersecond':
            return value  / 60 ; // 1 m³/s = 60 m³/min
        case 'litersperhour':
            return value  * 1000 * 60; //
        case 'litersperminute':
            return value * 1000; // 
        case 'literspersecond':
            return value * 1000/60; // 
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
function convertFromCubicMeterPerSecond(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'cubicmeterperhour':
            return value * 3600; // 1 m³/s = 3600 m³/h
        case 'cubicmeterperminute':
            return value * 60; // 1 m³/s = 60 m³/min
        case 'cubicmeterpersecond':
            return value * 1 ; // 1 m³/s = 1 m³/s
        case 'litersperhour':
            return value * 1000 * 3600; // 1 m³/s = 3.600.000 l/h
        case 'litersperminute':
            return value * 1000 * 60 ; // 1 m³/s = 60.000 l/min
        case 'literspersecond':
            return value * 1000; //  1m³/s = 1000 l/s
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
function convertFromLiterPerHour(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'cubicmeterperhour':
            return value / 1000; // 
        case 'cubicmeterperminute':
            return value / 1000 / 60; // 
        case 'cubicmeterpersecond':
            return value  / 1000 / 3600 ; //
        case 'litersperhour':
            return value *1; //
        case 'litersperminute':
            return value / 60; // 
        case 'literspersecond':
            return value / 3600; // 
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
function convertFromLiterPerMinute(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'cubicmeterperhour':
            return value / 1000 * 60; // 
        case 'cubicmeterperminute':
            return value / 1000; // 
        case 'cubicmeterpersecond':
            return value  / 1000 /60 ; // 60*60 = 3600
        case 'litersperhour':
            return value * 60; //
        case 'litersperminute':
            return value * 1; // 
        case 'literspersecond':
            return value / 60; // 
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
function convertFromLiterPerSecond(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'cubicmeterperhour':
            return value / 1000 * 3600; // 
        case 'cubicmeterperminute':
            return value / 1000 * 60; // 
        case 'cubicmeterpersecond':
            return value  / 1000 ; // 60*60 = 3600
        case 'litersperhour':
            return value * 60 * 60; //
        case 'litersperminute':
            return value * 60; // 
        case 'literspersecond':
            return value * 1; // 
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
//--------------------------------------------------------------------------------------------------
// function "Massa"
function convertFromKiloGram(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'kilogram':
            return value * 1; // 1kG = 1 kG
        case 'gram':
            return value * 1000; // 1000g = 1kg
        case 'milligram':
            return value * 1000 * 1000 ; // 1.000.000 mg = 1kg 
        case 'ton':
            return value / 1000; // 1000 kg = 1 ton
        case 'pond':
            return value * 2.20462; //
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
function convertFromGram(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'kilogram':
            return value / 1000; // 1kG = 1 kG
        case 'gram':
            return value * 1; // 1000g = 1kg
        case 'milligram':
            return value * 1000 ; // 1.000.000 mg = 1kg 
        case 'ton':
            return value / 1000 /1000; // 1000 kg = 1 ton
        case 'pond':
            return value * 2.20462 / 1000; //
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
function convertFromMilliGram(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'kilogram':
            return value / 1000 /1000; // 1kG = 1 kG
        case 'gram':
            return value /1000; // 1000g = 1kg
        case 'milligram':
            return value * 1 ; // 1.000.000 mg = 1kg 
        case 'ton':
            return value / 1000 / 1000 / 1000; // 1000 kg = 1 ton
        case 'pond':
            return value * 2.20462 / 1000 / 1000; //
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}

function convertFromTon(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'kilogram':
            return value *1000; // 1kG = 1 kG
        case 'gram':
            return value * 1000* 1000; // 1000g = 1kg
        case 'milligram':
            return value * 1000 * 1000* 1000 ; // 1.000.000 mg = 1kg 
        case 'ton':
            return value * 1; // 1000 kg = 1 ton
        case 'pond':
            return value * 2.20462 *1000 ; //
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
function convertFromPond(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'kilogram':
            return value / 2.20462; // 1kG = 1 kG
        case 'gram':
            return value / 2.20462 *1000; // 1000g = 1kg
        case 'milligram':
            return value / 2.20462 * 1000 * 1000; // 1.000.000 mg = 1kg 
        case 'ton':
            return value / 2.20462 / 1000; // 1000 kg = 1 ton
        case 'pond':
            return value * 1 ; //
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
//--------------------------------------------------------------------------------------------------
// function "Energie"
function convertFromJoules(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'joules':
            return value * 1; //
        case 'kilojoules':
            return value / 1000; // 
        case 'kilowattuur':
            return value / 3600 / 1000 ; // 
        case 'wattuur':
            return value / 3600; // 
        case 'wattseconde':
            return value * 1; // 
        case 'britishthermalunit':
            return value / 1055.05585; // 
        case 'calorie':
            return value * 0.2388; // 
        case 'kilocalorie':
            return value * 0.2388 / 1000; // 
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
function convertFromKiloJoules(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'joules':
            return value * 1000; //
        case 'kilojoules':
            return value * 1; // 
        case 'kilowattuur':
            return value / 3600 ; // 
        case 'wattuur':
            return value / 3600 * 1000; // 
        case 'wattseconde':
            return value * 1000 ; // 
        case 'britishthermalunit':
            return value / 1055.05585 * 1000; // 
        case 'calorie':
            return value * 0.2388 * 1000; // 
        case 'kilocalorie':
            return value * 0.2388 ; // 
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
function convertFromKiloWattUur(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'joules':
            return value * 3600 * 1000 ; //
        case 'kilojoules':
            return value * 3600; // 
        case 'kilowattuur':
            return value * 1 ; // 
        case 'wattuur':
            return value * 1000; // 
        case 'wattseconde':
            return value * 1000 * 3600; // 
        case 'britishthermalunit':
            return value * 3412.13; // 
        case 'calorie':
            return value * 859845; // 
        case 'kilocalorie':
            return value * 859.845; // 
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
function convertFromWattUur(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'joules':
            return value * 3600  ; //
        case 'kilojoules':
            return value * 3600 / 1000; // 
        case 'kilowattuur':
            return value / 1000 ; // 
        case 'wattuur':
            return value * 1000; // 
        case 'wattseconde':
            return value * 3600; // 
        case 'britishthermalunit':
            return value * 3412.13 / 1000; // 
        case 'calorie':
            return value * 859.845; // 
        case 'kilocalorie':
            return value * 859.845 / 1000; // 
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
function convertFromWattSeconde(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'joules':
            return value * 1  ; //
        case 'kilojoules':
            return value / 1000; // 
        case 'kilowattuur':
            return value / 1000 / 3600 ; // 
        case 'wattuur':
            return value / 3600; // 
        case 'wattseconde':
            return value * 1; // 
        case 'britishthermalunit':
            return value *  0.0009478; // 
        case 'calorie':
            return value * 0.2388; // 
        case 'kilocalorie':
            return value * 0.2388 / 1000; // 
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
function convertFromBritishThermalUnit(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'joules':
            return value * 1055.06  ; //
        case 'kilojoules':
            return value * 1055.06 / 1000; // 
        case 'kilowattuur':
            return value * 0.00029307 ; // 
        case 'wattuur':
            return value * 0.29307; // 
        case 'wattseconde':
            return value * 1055.06; // 
        case 'britishthermalunit':
            return value *  1; // 
        case 'calorie':
            return value * 251.996; // 
        case 'kilocalorie':
            return value * 251.996 / 1000; // 
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
function convertFromCalorie(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'joules':
            return value * 4.1868 ; //
        case 'kilojoules':
            return value * 4.1868 / 1000; // 
        case 'kilowattuur':
            return value * 0.000001163 ; // 
        case 'wattuur':
            return value * 0.001163; // 
        case 'wattseconde':
            return value * 4.1868; // 
        case 'britishthermalunit':
            return value *  0.003968; // 
        case 'calorie':
            return value * 1; // 
        case 'kilocalorie':
            return value / 1000; // 
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}
function convertFromKiloCalorie(value, toUnit) {
    // Return the converted value
    switch (toUnit) {
        case 'joules':
            return value * 4.1868 * 1000 ; //
        case 'kilojoules':
            return value * 4.1868 ; // 
        case 'kilowattuur':
            return value * 0.000001163 * 1000 ; // 
        case 'wattuur':
            return value * 0.001163 * 1000; // 
        case 'wattseconde':
            return value * 4.1868 * 1000; // 
        case 'britishthermalunit':
            return value *  0.003968 * 1000; // 
        case 'calorie':
            return value * 1000; // 
        case 'kilocalorie':
            return value *1 ; // 
        // Add more cases for other units as needed
        default:
            return 'Invalid unit';
    }
}

