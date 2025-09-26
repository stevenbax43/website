// -------------------------
// Utilities / poly-guards
// -------------------------
const byId = (id) => document.getElementById(id);
const on = (el, evt, fn) => el && el.addEventListener(evt, fn);

// -------------------------
// Persist inputs
// -------------------------
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
      if (savedValue !== null) field.value = savedValue;
    }
  });
}

// -------------------------
// Process state
// -------------------------
let currentProces = 1;
const minProces = 1;
const maxProces = 4;

// -------------------------
// UI: show/hide per process
// -------------------------
function showDropdownProces(idx) {
  const procesSel = byId(`proces${idx}`);
  if (!procesSel) return;

  const proces = procesSel.value;

  // dropdowns + containers
  const funcEl        = byId(`proces${idx}_func`);
  const func2El       = byId(`proces${idx}_func2`);
  const func_container   = byId(`proces${idx}_func_container`);
  const func_2_container = byId(`proces${idx}_func2_container`);
  const func   = funcEl  ? funcEl.value  : '';
  const func_2 = func2El ? func2El.value : '';

  updateProcesLineColor(proces, idx);
  updateProcesContainerColor(`proces${idx}`);
  updateChartLineVisibility(currentProces);
  saveInputValues(); // Save current state before making changes

  // Value containers
  const values = Array.from({ length: 9 }, (_, j) => byId(`Proces${idx}_value${j + 1}_container`));

  // Hide all value containers
  values.forEach(v => {
    if (v) { v.style.display = 'none'; v.style.visibility = 'hidden'; }
  });

  // Hide all unit spans
  ['powerHeatUnit', 'DeltaTUnit', 'DeltaHUnit', 'ToTUnit', 'AdXUnit', 'AdRHUnit'].forEach(type => {
    const el = byId(`${type}${idx}`);
    if (el) el.style.display = 'none';
  });

  // Hide function dropdowns by default
  if (func_container) { func_container.style.display = 'none'; func_container.style.visibility = 'hidden'; }
  if (func_2_container) func_2_container.style.display = 'none';

  // -- Main Process Logic --
  if (proces === 'selectProces') {
    if (func_container) { func_container.style.display = 'inline-block'; func_container.style.visibility = 'hidden'; }
    return;
  }

  if (proces === 'heat' || proces === 'cool') {
    if (func_container) { func_container.style.display = 'inline-block'; func_container.style.visibility = 'visible'; }

    if (proces === 'heat') {
      // show only value2
      if (values[0]) { values[0].style.display = 'inline-block'; values[0].style.visibility = 'hidden'; }
      if (values[1]) { values[1].style.display = 'inline-block'; values[1].style.visibility = 'visible'; }
    } else {
      // cool → show both value1 & value2
      [values[0], values[1]].forEach(v => {
        if (v) { v.style.display = 'inline-block'; v.style.visibility = 'visible'; }
      });
    }
  }

  if (proces === 'humid') {
    if (func_2_container) { func_2_container.style.display = 'inline-block'; func_2_container.style.visibility = 'visible'; }
    if (values[0]) { values[0].style.display = 'inline-block'; values[0].style.visibility = 'hidden'; }
    if (values[1]) { values[1].style.display = 'inline-block'; values[1].style.visibility = 'visible'; }
  }

  if (proces === 'mix') {
    if (func_container) { func_container.style.display = 'inline-block'; func_container.style.visibility = 'hidden'; }
    ['value3','value4','value5','value6'].forEach(v => {
      const el = byId(`Proces${idx}_${v}_container`);
      if (el) { el.style.display = 'inline-block'; el.style.visibility = 'visible'; }
    });
  }

  if (proces === 'heat_rec') {
    if (func_container) { func_container.style.display = 'inline-block'; func_container.style.visibility = 'hidden'; }
    // hide 3 & 5
    ['value3','value5'].forEach(v => { const el = byId(`Proces${idx}_${v}_container`); if (el) el.style.display = 'none'; });
    // show 4,6,7,8
    ['value4','value6','value7','value8'].forEach(v => {
      const el = byId(`Proces${idx}_${v}_container`);
      if (el) { el.style.display = 'inline-block'; el.style.visibility = 'visible'; }
    });
  }

  if (proces === 'cust_point') {
    if (func_container) { func_container.style.display = 'inline-block'; func_container.style.visibility = 'hidden'; }
    if (values[8]) { values[8].style.display = 'inline-block'; values[8].style.visibility = 'visible'; }
    if (values[5]) { values[5].style.display = 'inline-block'; values[5].style.visibility = 'visible'; }
  }

  // -- Units (func-dependent) --
  const showUnit = (id) => { const el = byId(`${id}${idx}`); if (el) el.style.display = 'inline-block'; };

  if (func_container && func_container.style.display !== 'none') {
    switch (func) {
      case 'power':  showUnit('powerHeatUnit'); break;
      case 'deltaT': showUnit('DeltaTUnit');    break;
      case 'deltaH': showUnit('DeltaHUnit');    break;
      case 'toTemp': showUnit('ToTUnit');       break;
    }
  }
  if (func_2_container && func_2_container.style.display !== 'none') {
    if (func_2 === 'AdiabaticX' || func_2 === 'IsoX')  showUnit('AdXUnit');
    if (func_2 === 'AdiabaticRH' || func_2 === 'IsoRH') showUnit('AdRHUnit');
  }
}

// -------------------------
// Visual container color
// -------------------------
function updateProcesContainerColor(selectId) {
  const sel = byId(selectId);
  const container = byId(`${selectId}_container`);
  const title = byId(`${selectId}_title`);
  if (!sel || !container || !title) return;

  const proces = sel.value;

  const classColorMap = {
    'heat': 'danger',
    'cool': 'primary',
    'humid': 'success',
    'mix': 'warning',
    'heat_rec': 'info',
    'selectProces': 'secondary'
  };
  const rgbColorMap = { 'cust_point': 'rgb(162, 0, 255)' };

  // Remove Bootstrap color classes
  container.className = container.className.replace(/\bborder-\w+\b/g, '').trim();
  title.className = title.className.replace(/\bbg-\w+\b/g, '').trim();

  container.classList.remove('border'); // reset default border
  container.style.border = title.style.backgroundColor = '';

  if (rgbColorMap[proces]) {
    const rgb = rgbColorMap[proces];
    container.style.border = `2px solid ${rgb}`;
    title.style.backgroundColor = rgb;
  } else {
    const color = classColorMap[proces] || 'light';
    container.classList.add('border', `border-${color}`);
    title.classList.add(`bg-${color}`);
  }
}

// -------------------------
// Chart helpers
// -------------------------
function updateProcesLineColor(selectedProcess, idx) {
  // persist selection for this step
  sessionStorage.setItem(`selectedProces${idx}`, selectedProcess);

  // chart color map
  const colorMap = {
    'heat':       'rgb(220, 53, 69)',
    'cool':       'rgb(0, 123, 255)',
    'humid':      'rgb(40, 167, 69)',
    'mix':        'rgb(255, 193, 7)',
    'heat_rec':   'rgb(23, 162, 184)',
    'cust_point': 'rgb(132, 0, 255)',
    'selectProces':'rgb(123, 108, 125)'
  };
  const color = colorMap[selectedProcess] || 'rgb(0,0,0)';

  // update chart line
  if (window.myLineChart?.data?.datasets) {
    const ds = myLineChart.data.datasets.find(d => d.label === `Proces ${idx}`);
    if (ds) { ds.borderColor = color; myLineChart.update(); }
  }

  // color only the Procesnaam cell in the table
  setProcessNameColorByStep(idx);
}
// -------------------------
// Table: color only the "Procesnaam" cell per step
// -------------------------
const procTextClassMap = {
  heat:        'text-danger',
  cool:        'text-primary',
  humid:       'text-success',
  mix:         'text-warning',
  heat_rec:    'text-info',
  cust_point:  'text-purple',   // needs a small CSS helper
  selectProces:'text-muted'
};
const ALL_PROC_TEXT_CLASSES = Object.values(procTextClassMap);

function setProcessNameColorByStep(step) {
  // find the row using the "proces_angle_temp_{step}" cell
  const angleCell = byId(`proces_angle_temp_${step}`);
  if (!angleCell) return;                     // row not rendered
  const row = angleCell.closest('tr');
  if (!row || !row.cells || !row.cells.length) return;

  const nameCell = row.cells[0];              // first cell = Procesnaam
  // pick the selected proces (sessionStorage first, then current select)
  const selected =
    sessionStorage.getItem(`selectedProces${step}`) ||
    byId(`proces${step}`)?.value ||
    'selectProces';

  // reset & apply class
  nameCell.classList.remove(...ALL_PROC_TEXT_CLASSES);
  nameCell.classList.add(procTextClassMap[selected] || 'text-muted');
}

function setAllProcessNameColors() {
  document.querySelectorAll('td[id^="proces_angle_temp_"]').forEach(td => {
    const step = td.id.replace('proces_angle_temp_', '');
    setProcessNameColorByStep(step);
  });
}



// Backward-compat shim: if called with no argument → recolor all visible processes
function updateLineColorChart(idx) {
  if (!window.myLineChart?.data?.datasets) return;

  // if a single idx was passed, honor it
  if (typeof idx === 'number') {
    const sel = sessionStorage.getItem(`selectedProces${idx}`) || byId(`proces${idx}`)?.value || 'selectProces';
    updateProcesLineColor(sel, idx);
    return;
  }
  // otherwise update all currently shown processes
  for (let i = 1; i <= currentProces; i++) {
    const sel = sessionStorage.getItem(`selectedProces${i}`) || byId(`proces${i}`)?.value || 'selectProces';
    updateProcesLineColor(sel, i);
  }
}

function updateChartLineVisibility(currentProces) {
  if (!window.myLineChart?.data?.datasets) return;

  myLineChart.data.datasets.forEach(dataset => {
    const label = dataset.label;

    if (label === 'Startpunt') {
      dataset.hidden = false;
      return;
    }
    if (dataset.isExtension) {
      dataset.hidden = (dataset.sourceProcesStep > currentProces);
      return;
    }
    if (label && label.startsWith('Proces')) {
      const stepNum = parseInt(label.split(' ')[1], 10);
      dataset.hidden = (stepNum > currentProces);
      return;
    }
    // RH / H background datasets always visible
    dataset.hidden = false;
  });

  myLineChart.update();
}

function updateProcesContainers() {
  for (let i = 1; i <= maxProces; i++) {
    const row = byId(`row-proces${i}`);
    if (row) row.style.display = (i <= currentProces) ? '' : 'none';
  }

  const hiddenInput = byId('currentProces');
  if (hiddenInput) hiddenInput.value = Array.from({ length: currentProces }, (_, i) => i + 1).join(',');

  const counter = byId('procesCounterLabel');
  if (counter) {
    counter.textContent = (currentProces === maxProces)
      ? `Verwijderen proces ${currentProces-1} -> ${maxProces}`
      : `Toevoegen van Proces ${currentProces} -> ${currentProces + 1}`;
  }

  const minus = byId('btn-minus');
  const plus  = byId('btn-plus');
  if (minus) minus.disabled = currentProces === minProces;
  if (plus)  plus.disabled  = currentProces === maxProces;
}

// -------------------------
// Start condition inputs
// -------------------------
const variableInfo = {
  'Tdb': { unit: '°C',     min: -10, max: 40,  default: 25.0, step: 0.1 },
  'RH':  { unit: '%',      min: 1,   max: 100, default: 50,   step: 0.1 },
  'AH':  { unit: 'g/kg',   min: 0.1, max: 20,  default: 5.0,  step: 0.1 },
  'h':   { unit: 'kJ/kg',  min: -5,  max: 90,  default: 40.0, step: 0.1 },
  'Twb': { unit: '°C',     min: -10, max: 30,  default: 18.0, step: 0.1 }
};

let prevSel1 = null;
let prevSel2 = null;

// cache after DOM is ready
let sel1, sel2, inp1, inp2, unit1, unit2;

function clampInput(inputElem, min, max) {
  const val = parseFloat(inputElem.value);
  if (isNaN(val)) return;
  if (val < min) inputElem.value = min;
  if (val > max) inputElem.value = max;
}

function shouldDisable(optionValue, otherSelectedValue, selfSelectedValue) {
  const isSame = optionValue === otherSelectedValue;
  const isConflicting =
    (optionValue === 'RH'  && otherSelectedValue === 'AH') ||
    (optionValue === 'AH'  && otherSelectedValue === 'RH') ||
    (optionValue === 'Twb' && otherSelectedValue === 'h')  ||
    (optionValue === 'h'   && otherSelectedValue === 'Twb');
  // never disable the current selected value
  if (optionValue === selfSelectedValue) return false;
  return isSame || isConflicting;
}

function updateSingleAirInput(selectElem, inputElem, unitElem, prevValKey) {
  if (!selectElem || !inputElem || !unitElem) return;

  const val = selectElem.value;

  if (val !== window[prevValKey] && variableInfo[val]) {
    if (!sessionStorage.getItem(inputElem.id)) {
      inputElem.value = variableInfo[val].default;
    }
  }
  if (variableInfo[val]) {
    const info = variableInfo[val];
    unitElem.textContent = info.unit;
    inputElem.min = info.min;
    inputElem.max = info.max;
    inputElem.step = info.step;
    clampInput(inputElem, info.min, info.max);
  }

  window[prevValKey] = val;
}

function updateSelectDisabling() {
  if (!sel1 || !sel2) return;
  const val1 = sel1.value;
  const val2 = sel2.value;

  Array.from(sel1.options).forEach(opt => {
    opt.disabled = shouldDisable(opt.value, val2, val1);
  });
  Array.from(sel2.options).forEach(opt => {
    opt.disabled = shouldDisable(opt.value, val1, val2);
  });
}

function updateAirStartInput1() {
  updateSingleAirInput(sel1, inp1, unit1, 'prevSel1');
  updateSelectDisabling();
}
function updateAirStartInput2() {
  updateSingleAirInput(sel2, inp2, unit2, 'prevSel2');
  updateSelectDisabling();
}

// -------------------------
// Init & Event wiring
// -------------------------
document.addEventListener('DOMContentLoaded', function () {
  // cache start-air elements after DOM is ready
  sel1  = byId('varStart1');
  sel2  = byId('varStart2');
  inp1  = byId('StartInput1');
  inp2  = byId('StartInput2');
  unit1 = byId('Startunit1');
  unit2 = byId('Startunit2');

  triggerMollierOnce();       // only first visit
  initAirInputs();
  restoreSessionData();

  const skipScrollRestore = sessionStorage.getItem('skipScrollOnLoad') === 'true';
  if (!skipScrollRestore) restoreScrollPosition();
  sessionStorage.removeItem('skipScrollOnLoad');

  initEventListeners();
});

function initProcesDropdowns() {
  for (let i = 1; i <= currentProces; i++) {
    showDropdownProces(i);
    setProcessNameColorByStep(i);
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

  // recolor all visible process lines (shim keeps the old name usable)
  updateLineColorChart();
  setAllProcessNameColors();  

}

function restoreScrollPosition() {
  const y = sessionStorage.getItem('scrollPosition');
  if (y) window.scrollTo(0, parseInt(y, 10));
  window.addEventListener('scroll', () => {
    sessionStorage.setItem('scrollPosition', window.scrollY);
  });
}

// Keep your header sanitizing helper as-is
function cloneAndConvertTableHeaders(originalTable) {
  if (!originalTable) return null;
  const cloned = originalTable.cloneNode(true);
  const ths = cloned.querySelectorAll('th');
  ths.forEach(th => {
    const original = th.innerHTML;
    const converted = original
      .replace(/<sub>(.*?)<\/sub>/g, (_, sub) => `_${sub}`)
      .replace(/<[^>]+>/g, '');
    th.textContent = converted;
  });
  return cloned;
}

function initEventListeners() {
  // Inputs → recalc + keep UI visibility logic
  document.querySelectorAll('input[type="number"]').forEach(field => {
    on(field, 'change', () => {
      saveInputValues();
      byId('mollierButton')?.click();
      setTimeout(initProcesDropdowns, 100);
    });
    setAllProcessNameColors();   
  });

  // Process +/- controls
  const btnPlus = byId('btn-plus');
  const btnMinus = byId('btn-minus');

  on(btnPlus, 'click', () => {
    if (currentProces < maxProces) {
      currentProces++;
      sessionStorage.setItem('currentProces', currentProces);
      updateProcesContainers();
      showDropdownProces(currentProces);
      updateChartLineVisibility(currentProces);
      setProcessNameColorByStep(currentProces);
    }
  });

  on(btnMinus, 'click', () => {
    if (currentProces > minProces) {
      currentProces--;
      sessionStorage.setItem('currentProces', currentProces);

      const stepToRemove = currentProces + 1;
      const prefix = `proces${stepToRemove}`;
      const inputIds = [prefix, `${prefix}_func`, `${prefix}_func2`];
      for (let j = 1; j <= 9; j++) inputIds.push(`Proces${stepToRemove}_value${j}`);
      inputIds.forEach(id => sessionStorage.removeItem(id));

      // Remove dataset and its extension from the chart (if present)
      if (window.myLineChart?.data?.datasets) {
        const labelToRemove = `Proces ${stepToRemove}`;
        myLineChart.data.datasets = myLineChart.data.datasets.filter(ds =>
          ds.label !== labelToRemove && !(ds.isExtension && ds.sourceProcesStep === stepToRemove)
        );
        myLineChart.update();
      }

      updateProcesContainers();
      updateChartLineVisibility(currentProces);
      setAllProcessNameColors();
    }
  });

  // Top intro buttons (guards keep things safe if HTML changes)
  on(byId('printButton'), 'click', () => window.print());
  on(byId('excelButton'), 'click', () => { if (window.pdfUrlExcel) window.open(pdfUrlExcel, '_blank'); });

  on(byId('SaveInputsButton'), 'click', () => {
    const projectName = prompt("Voer projectnaam in:");
    if (projectName && projectName.trim() !== "") sendSessionStorageToDjango(projectName.trim());
  });

  on(byId('LoadInputsButton'), 'click', () => {
    if (window.bootstrap?.Modal) {
      const modal = new bootstrap.Modal(byId('loadProjectModal'));
      modal.show();
    }
  });

  on(byId('SavePDFButton'), 'click', () => {
    const tablePoints = document.querySelector('#table_points')?.closest('.card-body')?.querySelector('table');
    const tableProces = document.querySelector('#table_proces')?.closest('.card-body')?.querySelector('table'); 
    if (!tablePoints || !tableProces) return;

    const grabTable = (table) => {
      const rows = table.querySelectorAll('thead tr, tbody tr');
      return Array.from(rows).map(row => {
        const cells = row.querySelectorAll('th, td');
        return Array.from(cells).map(c => c.innerText.trim());
      });
    };

    const tableDataPoints = grabTable(tablePoints);
    const tableDataProces = grabTable(tableProces);

    const canvas = byId("myLinesRH");
    if (!canvas) return;

    const scale = 3;
    const exportCanvas = document.createElement("canvas");
    exportCanvas.width = canvas.width * scale;
    exportCanvas.height = canvas.height * scale;

    const exportCtx = exportCanvas.getContext("2d");
    exportCtx.fillStyle = "#FFFFFF"; exportCtx.fillRect(0,0,exportCanvas.width,exportCanvas.height);
    exportCtx.scale(scale, scale); exportCtx.drawImage(canvas, 0, 0);

    const base64 = exportCanvas.toDataURL("image/png").split(',')[1];

    byId("table_points_json").value  = JSON.stringify(tableDataPoints);
    byId("table_process_json").value = JSON.stringify(tableDataProces);
    byId("chart_image_base64").value = base64;

    const pdfUrl = byId("SavePDFButton")?.dataset?.pdfUrl;
    const form = byId("inputForm");
    if (!pdfUrl || !form) return;

    form.action = pdfUrl;
    form.method = "post";

    // include a hidden flag for the backend
    const hiddenButtonInput = document.createElement("input");
    hiddenButtonInput.type = "hidden";
    hiddenButtonInput.name = "SavePDFButton";
    hiddenButtonInput.value = "clicked";
    form.appendChild(hiddenButtonInput);

    form.submit();
    form.removeChild(hiddenButtonInput);
  });
}

// -------------------------
// First-time trigger
// -------------------------
function triggerMollierOnce() {
  if (!sessionStorage.getItem('mollierInitialized')) {
    byId('mollierButton')?.click();
    sessionStorage.setItem('mollierInitialized', 'true');
  }
}

// -------------------------
// AJAX calls
// -------------------------
function sendSessionStorageToDjango(projectName) {
  const sessionData = {};
  for (let i = 0; i < sessionStorage.length; i++) {
    const key = sessionStorage.key(i);
    sessionData[key] = sessionStorage.getItem(key);
  }

  fetch("{% url 'tools:save_project' %}", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
    },
    body: JSON.stringify({ projectname: projectName, sessionstorage: sessionData })
  })
  .then(r => r.json())
  .then(() => alert("Opgeslagen!"))
  .catch(err => { console.error(err); alert("Fout bij opslaan"); });
}

function loadSavedProject(projectId) {
  fetch("{% url 'tools:load_project' %}", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    },
    body: JSON.stringify({ project_id: projectId })
  })
  .then(r => r.json())
  .then(data => { if (data.status === 'ok') location.reload(); else alert('❌ ' + (data.message || 'Fout bij laden')); })
  .catch(err => { console.error(err); alert('⚠️ Verbindingsfout'); });
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    document.cookie.split(';').forEach(c => {
      c = c.trim();
      if (c.startsWith(name + '=')) cookieValue = decodeURIComponent(c.slice(name.length + 1));
    });
  }
  return cookieValue;
}

function deleteProject(projectId) {
  if (!confirm("Weet je zeker dat je dit project wilt verwijderen?")) return;

  fetch("{% url 'tools:delete_project' %}", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    },
    body: JSON.stringify({ project_id: projectId })
  })
  .then(r => { if (!r.ok) throw new Error(`Server returned ${r.status}`); return r.json(); })
  .then(data => { if (data.status === 'deleted') location.reload(); else alert('❌ ' + (data.message || 'Fout bij verwijderen')); })
  .catch(err => { console.error(err); alert('⚠️ Verbindings- of serverfout bij verwijderen'); });
}

