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
let currentProces = 1;
const minProces = 1;
const maxProces = 4;

function showDropdownProces(idx) {
    const proces = document.getElementById(`proces${idx}`).value;
    updateProcesLineColor(proces, idx);
    updateProcesContainerColor(`proces${idx}`);
    updateChartLineVisibility(currentProces);
    const func = document.getElementById(`proces${idx}_func`).value;
    const func_2 = document.getElementById(`proces${idx}_func2`).value;

    const func_container = document.getElementById(`proces${idx}_func_container`);
    const func_2_container = document.getElementById(`proces${idx}_func2_container`);
    saveInputValues(); // Save current state before making changes
    // Value containers
    const values = Array.from({ length: 9 }, (_, j) =>
        document.getElementById(`Proces${idx}_value${j + 1}_container`)
    );

    // Hide all value containers
    values.forEach(v => {
        if (v) {
            v.style.display = 'none';
            v.style.visibility = 'hidden';
        }
    });

    // Hide all unit spans
    const unitTypes = ['powerHeatUnit', 'DeltaTUnit', 'DeltaHUnit', 'ToTUnit', 'AdXUnit', 'AdRHUnit'];
    unitTypes.forEach(type => {
        const el = document.getElementById(`${type}${idx}`);
        if (el) el.style.display = 'none';
    });

    // Hide function dropdowns by default
    func_container.style.display = 'none';
    func_container.style.visibility = 'hidden';
    func_2_container.style.display = 'none';

    // -- Main Process Logic --
    if (proces === 'selectProces') {
        if (func_container) {
            func_container.style.display = 'inline-block'; // ✅ ADD THIS
            func_container.style.visibility = 'hidden';
        }
        return; // Exit early if nothing selected
    }

    if (proces === 'heat' || proces === 'cool') {
    func_container.style.display = 'inline-block';
    func_container.style.visibility = 'visible';

        if (proces === 'heat') {
            // Hide value0, show value1
            if (values[0]) {
                values[0].style.display = 'inline-block'; // ✅ ADD THIS
                values[0].style.visibility = 'hidden';
            }
            if (values[1]) {
                values[1].style.display = 'inline-block';
                values[1].style.visibility = 'visible';
            }
        }

        if (proces === 'cool') {
            // Show both value0 and value1
            [values[0], values[1]].forEach(v => {
                if (v) {
                    v.style.display = 'inline-block';
                    v.style.visibility = 'visible';
                }
            });
        }
    }

    if (proces === 'humid') {
    func_2_container.style.display = 'inline-block';

        // Hide value0 only using visibility
        if (values[0]) {
            values[0].style.display = 'inline-block'; // ✅ ADD THIS
            values[0].style.visibility = 'hidden';
        }

        // Show value1 using both visibility and display
        if (values[1]) {
            values[1].style.display = 'inline-block'; // ✅ ADD THIS
            values[1].style.visibility = 'visible';
        }
    }
    if (proces === 'mix') {
        func_container.style.display = 'inline-block';
        func_container.style.visibility = 'hidden';
        ['value3', 'value4', 'value5', 'value6'].forEach((v, i) => {
            const el = document.getElementById(`Proces${idx}_${v}_container`);
            if (el) {
                el.style.display = 'inline-block';
                el.style.visibility = 'visible';
            }
        });
    }

    if (proces === 'heat_rec') {
        func_container.style.display = 'inline-block';
        func_container.style.visibility = 'hidden';

        // Hide 3 and 5, show 7 and 8
        const toHide = ['value3', 'value5'];
        const toShow = ['value4', 'value6', 'value7', 'value8'];
        toHide.forEach(v => {
            const el = document.getElementById(`Proces${idx}_${v}_container`);
            if (el) el.style.display = 'none';
        });
        toShow.forEach(v => {
            const el = document.getElementById(`Proces${idx}_${v}_container`);
            if (el) {
                el.style.display = 'inline-block';
                el.style.visibility = 'visible';
            }
        });
    }

    if (proces === 'cust_point') {
        func_container.style.display = 'inline-block';
        func_container.style.visibility = 'hidden';
        values[8].style.display = 'inline-block';
        values[8].style.visibility = 'visible';
        values[5].style.display = 'inline-block';
        values[5].style.visibility = 'visible';
    }

    // -- Units (func-dependent) --
    const showUnit = (id) => {
        const el = document.getElementById(`${id}${idx}`);
        if (el) el.style.display = 'inline-block';
    };

    if (func_container.style.display !== 'none') {
        switch (func) {
            case 'power': showUnit('powerHeatUnit'); break;
            case 'deltaT': showUnit('DeltaTUnit'); break;
            case 'deltaH': showUnit('DeltaHUnit'); break;
            case 'toTemp': showUnit('ToTUnit'); break;
        }
    }

    if (func_2_container.style.display !== 'none') {
        if (func_2 === 'AdiabaticX' || func_2 === 'IsoX') showUnit('AdXUnit');
        if (func_2 === 'AdiabaticRH' || func_2 === 'IsoRH') showUnit('AdRHUnit');
    }
}
function updateProcesContainerColor(selectId) {
    const proces = document.getElementById(selectId).value;
    const container = document.getElementById(`${selectId}_container`);
    const title = document.getElementById(`${selectId}_title`);

    // Bootstrap-compatible color mappings
    const classColorMap = {
        'heat': 'danger',
        'cool': 'primary',
        'humid': 'success',
        'mix': 'warning',
        'heat_rec': 'info',
        'selectProces': 'secondary'
    };

    // Custom RGB color mappings
    const rgbColorMap = {
        'cust_point': 'rgb(162, 0, 255)' // Purple
    };

    // Remove Bootstrap color classes
    container.className = container.className.replace(/\bborder-\w+\b/g, '').trim();
    title.className = title.className.replace(/\bbg-\w+\b/g, '').trim();

    // Remove default Bootstrap border if present
    container.classList.remove('border');

    // Reset any inline styles
    container.style.border = '';
    container.style.borderColor = '';
    container.style.borderWidth = '';
    container.style.borderStyle = '';
    title.style.backgroundColor = '';

    if (rgbColorMap[proces]) {
        // Apply custom RGB border
        const rgb = rgbColorMap[proces];
        container.style.border = `2px solid ${rgb}`;
        title.style.backgroundColor = rgb;
    } else {
        // Apply Bootstrap class-based color
        const color = classColorMap[proces] || 'light';
        container.classList.add(`border-${color}`);
        container.classList.add('border'); // Re-add basic border for visibility
        title.classList.add(`bg-${color}`);
    }
}
function updateProcesLineColor(selectedProcess,idx) {
    const colorMap = {
        'heat': 'rgb(220, 53, 69)',      // danger
        'cool': 'rgb(0, 123, 255)',      // primary
        'humid': 'rgb(40, 167, 69)',     // success
        'mix': 'rgb(255, 193, 7)',       // warning
        'heat_rec': 'rgb(23, 162, 184)', // info
        'cust_point': 'rgb(132, 0, 255)',
        'selectProces': 'rgb(123, 108, 125)'
    };

    const color = colorMap[selectedProcess] || 'rgb(0, 0, 0)';

    // Find 'Proces' dataset and update its color
    const dataset = myLineChart.data.datasets.find(d => d.label === `Proces ${idx}`);
    if (dataset) {
        dataset.borderColor = color;
        myLineChart.update();
    }
}
function updateChartLineVisibility(currentProces) {
    if (!window.myLineChart || !myLineChart.data) return;
    myLineChart.data.datasets.forEach(dataset => {
        const label = dataset.label;

        if (label === 'Startpunt') {
            dataset.hidden = false;
        } else if (dataset.isExtension) {
            // Show/hide based on the source proces step
            dataset.hidden = dataset.sourceProcesStep > currentProces;
        } else if (label && label.startsWith('Proces')) {
            const stepNum = parseInt(label.split(' ')[1], 10);
            dataset.hidden = stepNum > currentProces;
        } else {
            dataset.hidden = false; // Always show RH, H, etc.
        }
    });

    myLineChart.update();
}
function updateProcesContainers() {
    for (let i = 1; i <= maxProces; i++) {
        const row = document.getElementById(`row-proces${i}`);
        if (row) {
            row.style.display = (i <= currentProces) ? '' : 'none';
        }
    }
    //  Add this line to update the hidden field
    const hiddenInput = document.getElementById('currentProces');
    if (hiddenInput) {
        hiddenInput.value = Array.from({ length: currentProces }, (_, i) => i + 1).join(',');
    }
    const counter = document.getElementById('procesCounterLabel');
    if (counter) {
        if (currentProces === maxProces) {
            counter.textContent = `Verwijderen proces ${currentProces-1} -> ${maxProces}`;
        } else {
            counter.textContent = `Toevoegen van Proces ${currentProces} -> ${currentProces + 1}`;
        }
    }

    const minus = document.getElementById('btn-minus');
    const plus = document.getElementById('btn-plus');
    if (minus) minus.disabled = currentProces === minProces;
    if (plus) plus.disabled = currentProces === maxProces;
}
const variableInfo = {
    'Tdb': { unit: '°C',     min: -10, max: 40,  default: 25.0, step: 0.1 },
    'RH':  { unit: '%',      min: 1,   max: 100, default: 50, step:0.1 },
    'AH':  { unit: 'g/kg',   min: 0.1,   max: 20,  default: 5.0,  step: 0.1 },
    'h':   { unit: 'kJ/kg',  min: -5,   max: 90,  default: 40.0, step: 0.1 },
    'Twb': { unit: '°C',     min: -10, max: 30,  default: 18.0, step: 0.1 }
};
// below inputs and constant for updateAirStartSelectInputs() function
let prevSel1 = null;
let prevSel2 = null;

// Cache DOM elements once
const sel1 = document.getElementById('varStart1');
const sel2 = document.getElementById('varStart2');
const inp1 = document.getElementById('StartInput1');
const inp2 = document.getElementById('StartInput2');
const unit1 = document.getElementById('Startunit1');
const unit2 = document.getElementById('Startunit2');

function clampInput(inputElem, min, max) {
    let val = parseFloat(inputElem.value);
    if (isNaN(val)) return;
    if (val < min) inputElem.value = min;
    if (val > max) inputElem.value = max;
}
function shouldDisable(optionValue, otherSelectedValue, selfSelectedValue) {
    const isSame = optionValue === otherSelectedValue;
    // Define invalid combinations
    const isConflicting =
        (optionValue === 'RH' && otherSelectedValue === 'AH') ||
        (optionValue === 'AH' && otherSelectedValue === 'RH') ||
        (optionValue === 'Twb' && otherSelectedValue === 'h') ||
        (optionValue === 'h' && otherSelectedValue === 'Twb');

    // 🔒 Never disable the current selected value
    if (optionValue === selfSelectedValue) return false;

    return isSame || isConflicting;
}
function updateSingleAirInput(selectElem, inputElem, unitElem, prevValKey) {
    const val = selectElem.value;

    if (val !== window[prevValKey] && variableInfo[val]) {
        if (!sessionStorage.getItem(inputElem.id)) {
            inputElem.value = variableInfo[val].default;
        }
    }

    if (variableInfo[val]) {
        unitElem.textContent = variableInfo[val].unit;
        inputElem.min = variableInfo[val].min;
        inputElem.max = variableInfo[val].max;
        inputElem.step = variableInfo[val].step;
        clampInput(inputElem, inputElem.min, inputElem.max);
    }

    window[prevValKey] = val;
}
function updateSelectDisabling() {
    const val1 = sel1.value;
    const val2 = sel2.value;

    Array.from(sel1.options).forEach(opt => {
        opt.disabled = shouldDisable(opt.value, val2);
    });

    Array.from(sel2.options).forEach(opt => {
        opt.disabled = shouldDisable(opt.value, val1);
    });
}
function updateAirStartInput1() {
    updateSingleAirInput(sel1, inp1, unit1, 'prevSel1');
    // Only disables conflicting values in sel2, not inp2
    updateSelectDisabling();
}
function updateAirStartInput2() {
    updateSingleAirInput(sel2, inp2, unit2, 'prevSel2');
    updateSelectDisabling();
}


document.addEventListener('DOMContentLoaded', function () {
    triggerMollierOnce();         // Only calls initProcesDropdowns() on first visit      
    initAirInputs();
    restoreSessionData();
    const skipScrollRestore = sessionStorage.getItem('skipScrollOnLoad') === 'true';
    if (!skipScrollRestore) {
        restoreScrollPosition();
    }
    sessionStorage.removeItem('skipScrollOnLoad'); // ✅ Clean up flag
    initEventListeners();
 
});

function initProcesDropdowns() { 
    for (let i = 1; i <= currentProces; i++) {
        showDropdownProces(i);
        updateProcesContainers();
    }
}

function initAirInputs() {
    updateAirStartInput1();
    updateAirStartInput2();
    updateSelectDisabling();
}

function restoreSessionData() {
    const savedProces = sessionStorage.getItem('currentProces');
    currentProces = Math.max(parseInt(savedProces || 1, 10), 1);
    loadInputValues();
    // Re-run to make sure state aligns with saved session values
    initAirInputs();
    initProcesDropdowns();
    updateLineColorChart();
}
const skipScrollRestore = sessionStorage.getItem('skipScrollOnLoad') === 'true';
function restoreScrollPosition() {
    const scrollPosition = sessionStorage.getItem('scrollPosition');
    if (scrollPosition) {
        window.scrollTo(0, parseInt(scrollPosition));
    }
    window.addEventListener('scroll', () => {
        sessionStorage.setItem('scrollPosition', window.scrollY);
    });
}
function cloneAndConvertTableHeaders(originalTable) {
    if (!originalTable) return null;

    const cloned = originalTable.cloneNode(true);
    const ths = cloned.querySelectorAll('th');

    ths.forEach(th => {
        const original = th.innerHTML;

        // Convert <sub>db</sub> to _db, remove any remaining tags
        const converted = original
            .replace(/<sub>(.*?)<\/sub>/g, (_, sub) => `_${sub}`)  // handle subscripts
            .replace(/<[^>]+>/g, ''); // strip any remaining tags (e.g. <b>, <i>)

        console.log(`✅ Header converted: "${original}" → "${converted}"`);
        th.textContent = converted;
    });

    return cloned;
}

function initEventListeners() {
    // Input change listeners
    document.querySelectorAll('input[type="number"]').forEach(field => {
        field.addEventListener('change', () => {
            saveInputValues();
            document.getElementById('mollierButton').click();
                    
            setTimeout(() => {
                initProcesDropdowns();  // Reapply visibility logic
            }, 100); 
        });
    });

    // Process counter logic
    const btnPlus = document.getElementById('btn-plus');
    const btnMinus = document.getElementById('btn-minus');
    if (btnPlus && btnMinus) {
        btnPlus.addEventListener('click', () => {
            if (currentProces < maxProces) {
                currentProces++;
                sessionStorage.setItem('currentProces', currentProces);
                updateProcesContainers();            // shows #row-procesX
                showDropdownProces(currentProces);   // initializes logic
                updateChartLineVisibility(currentProces); 
            }
        });

        btnMinus.addEventListener('click', () => {
            if (currentProces > minProces) {
                currentProces--;
                sessionStorage.setItem('currentProces', currentProces);

                const stepToRemove = currentProces + 1;
                const prefix = `proces${stepToRemove}`;
                const inputIds = [
                    prefix,
                    `${prefix}_func`,
                    `${prefix}_func2`
                ];
                for (let j = 1; j <= 9; j++) {
                    inputIds.push(`Proces${stepToRemove}_value${j}`);
                }
                inputIds.forEach(id => sessionStorage.removeItem(id));

                // ✅ Remove dataset and its extension from the chart
                const labelToRemove = `Proces ${stepToRemove}`;
                myLineChart.data.datasets = myLineChart.data.datasets.filter(ds => ds.label !== labelToRemove);
                myLineChart.data.datasets = myLineChart.data.datasets.filter(ds => !(ds.isExtension && ds.sourceProcesStep === stepToRemove));
                myLineChart.update();

                updateProcesContainers();
                
                updateChartLineVisibility(currentProces);
            }
        });
    
    }
   
    // Other UI buttons
    document.getElementById('readMeButton').addEventListener('click', () => {
        window.open(pdfUrlReadMe, '_blank');
    });

    document.getElementById('printButton').addEventListener('click', () => {
        window.print();
    });

    document.getElementById('excelButton').addEventListener('click', () => {
        window.open(pdfUrlExcel, '_blank');
    });
    document.getElementById('SaveInputsButton').addEventListener('click', () => {
        const projectName = prompt("Voer projectnaam in:");
        if (projectName && projectName.trim() !== "") {
            sendSessionStorageToDjango(projectName.trim());
        }
    });
    document.getElementById('LoadInputsButton').addEventListener('click', () => {
        const modal = new bootstrap.Modal(document.getElementById('loadProjectModal'));
        modal.show();
    });
    document.getElementById("SavePDFButton").addEventListener("click", () => {

        // 0. Get the table after #table_points
        const tablePoints = document.querySelector('#table_points + table');
        const allRowsPoints = tablePoints.querySelectorAll("thead tr, tbody tr");  // ✅ include headers and body

        const tableDataPoints = [];

        allRowsPoints.forEach(row => {
            const cells = row.querySelectorAll("th, td");  // ✅ handle both header and data cells
            const rowData = [];
            cells.forEach(cell => {
                rowData.push(cell.innerText.trim());
            });
            tableDataPoints.push(rowData);
        });

        // 1. Get the table after #table_proces
        const tableProces = document.querySelector('#table_proces + table');
        const allRowsProces = tableProces.querySelectorAll("thead tr, tbody tr");  // ✅ include headers and body

        const tableDataProces = [];

        allRowsProces.forEach(row => {
            const cells = row.querySelectorAll("th, td");  // ✅ handle both header and data cells
            const rowData = [];
            cells.forEach(cell => {
                rowData.push(cell.innerText.trim());
            });
            tableDataProces.push(rowData);
        });

        // 2. Convert canvas to base64 
        const canvas = document.getElementById("myLinesRH");
                
        // Create a temporary high-res canvas
        const scale = 3;// Try 2–4 for higher DPI
        const exportCanvas = document.createElement("canvas");
        exportCanvas.width = canvas.width * scale;
        exportCanvas.height = canvas.height * scale;

        const exportCtx = exportCanvas.getContext("2d");

        // White background
        exportCtx.fillStyle = "#FFFFFF";
        exportCtx.fillRect(0, 0, exportCanvas.width, exportCanvas.height);

        // Scale drawing
        exportCtx.scale(scale, scale);
        exportCtx.drawImage(canvas, 0, 0);

        // Convert to base64
        const base64 = exportCanvas.toDataURL("image/png").split(',')[1];

        // 3. Fill hidden fields
        document.getElementById("table_points_json").value = JSON.stringify(tableDataPoints);
        document.getElementById("table_process_json").value = JSON.stringify(tableDataProces);
        document.getElementById("chart_image_base64").value = base64;

        // 4. Update form action and submit
        const button = document.getElementById("SavePDFButton");
        const pdfUrl = button.dataset.pdfUrl;
        const form = document.getElementById("inputForm");
        form.action = pdfUrl;
        form.method = "post";
        
        // 5. Include button click explicitly in POST
        const hiddenButtonInput = document.createElement("input");
        hiddenButtonInput.type = "hidden";
        hiddenButtonInput.name = "SavePDFButton";
        hiddenButtonInput.value = "clicked";
        form.appendChild(hiddenButtonInput);
        
        //7. Submit the form to Django backend Python
        form.submit();
        // Reset after submission
        form.removeChild(hiddenButtonInput);
    });
    
}

function triggerMollierOnce() {
    if (!sessionStorage.getItem('mollierInitialized')) {
        document.getElementById('mollierButton').click();
        sessionStorage.setItem('mollierInitialized', 'true');

    }
}

function sendSessionStorageToDjango(projectName) {
    const sessionData = {};
    for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        sessionData[key] = sessionStorage.getItem(key);
    }

    fetch(saveProjectUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            projectname: projectName,
            sessionstorage: sessionData
        })
    })
    .then(response => response.json())
    .then(data => {
        alert("Opgeslagen!");
        // optionally reload or update modal
    })
    .catch(error => {
        alert("Fout bij opslaan");
        console.error(error);
    });
}
function loadSavedProject(projectId) {
    fetch(loadProjectUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ project_id: projectId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'ok') {
            // Page will reload and server will inject sessionStorage into template
            location.reload();
        } else {
            alert('❌ ' + (data.message || 'Fout bij laden'));
        }
    })
    .catch(err => {
        alert('⚠️ Verbindingsfout');
        console.error(err);
    });
}
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      document.cookie.split(';').forEach(cookie => {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
        }
      });
    }
    return cookieValue;
}
 function deleteProject(projectId) {
  // 1) Ask for confirmation
  if (!confirm("Weet je zeker dat je dit project wilt verwijderen?")) {
    return;
  }

  // 2) Grab CSRF token from your template’s hidden <input name="csrfmiddlewaretoken">
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  // 3) Fire the POST
  fetch(deleteProjectUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({ project_id: projectId })
  })
  // 4) Parse JSON
  .then(response => {
    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    if (data.status === 'deleted') {
      // success → reload so your server can re-inject sessionStorage / flash messages
      location.reload();
    } else {
      alert('❌ ' + (data.message || 'Fout bij verwijderen'));
    }
  })
  .catch(err => {
    console.error(err);
    alert('⚠️ Verbindings- of serverfout bij verwijderen');
  });
}