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
// ---- Helpers ----
function getActiveBlock() {
  const blocks = document.querySelectorAll('.maintoola2');
  for (const b of blocks) {
    if (getComputedStyle(b).display !== 'none') return b;
  }
  // Fallback: first block or #drukcontainer
  return document.getElementById('drukcontainer') || blocks[0] || null;
}

function formatNumber(n) {
  // Reasonable default: up to 10 significant digits, avoid scientific unless needed
  try {
    return Number(n).toLocaleString('en-US', { maximumSignificantDigits: 10 });
  } catch {
    return String(n);
  }
}
// ---- Core convert ----
function convert() {
  const targetDiv = getActiveBlock();
  if (!targetDiv) return;

  const valueEl     = targetDiv.querySelector('#value');
  const fromEl      = targetDiv.querySelector('#from');
  const toEl        = targetDiv.querySelector('#to');
  const magnitudeEl = targetDiv.querySelector('#magnitude');
  const outEl       = targetDiv.querySelector('#result, #output, .output');

  if (!valueEl || !fromEl || !toEl || !magnitudeEl || !outEl) return;

  const raw = parseFloat(valueEl.value);
  if (isNaN(raw)) { outEl.textContent = ''; return; }

  const magnitude = magnitudeEl.textContent.trim();
  const fromUnit  = fromEl.value;
  const toUnit    = toEl.value;

  const table = conversion_table[magnitude];
  if (!table || table[fromUnit] == null || table[toUnit] == null) {
    console.error('Unsupported conversion:', magnitude, fromUnit, '→', toUnit);
    return;
  }

  const fromToBase = table[fromUnit];
  const toToBase   = table[toUnit];
  const factor     = toToBase / fromToBase;
  const result     = raw * factor;

  // <output> supports .value; textContent also fine
  if ('value' in outEl) outEl.value = formatNumber(result);
  else outEl.textContent = formatNumber(result);
}


// ---- Category (pills) click handling ----
const categoryList = document.getElementById('categoryList');
if (categoryList) {
  categoryList.addEventListener('click', (event) => {
    const li = event.target.closest('.a2-pill');
    if (!li) return;

    const targetDivId = li.getAttribute('data-target');
    const blocks = document.querySelectorAll('.maintoola2');
    blocks.forEach(div => { div.style.display = 'none'; });

    const targetDiv = document.getElementById(targetDivId);
    if (targetDiv) {
      targetDiv.style.display = 'block'; // not flex; bootstrap rows handle layout
      // optional: set active pill styling
      categoryList.querySelectorAll('.a2-pill').forEach(p => p.classList.remove('active'));
      li.classList.add('active');
      convert();
    }
  });
}
// ---- Attach input/change listeners inside each block ----
document.querySelectorAll('.maintoola2').forEach((div) => {
  const val = div.querySelector('#value');
  const f   = div.querySelector('#from');
  const t   = div.querySelector('#to');
  if (val) val.addEventListener('input',  convert);
  if (f)   f.addEventListener('change', convert);
  if (t)   t.addEventListener('change', convert);
});


// ---- Other buttons + initial compute ----
document.addEventListener('DOMContentLoaded', () => {
  const printBtn = document.getElementById('printButton');
  if (printBtn) printBtn.addEventListener('click', () => window.print());

  const excelBtn = document.getElementById('excelButton');
  if (excelBtn) excelBtn.addEventListener('click', () => window.open(pdfUrlExcel, '_blank'));

  // Ensure one block is visible on load (your HTML currently shows #drukcontainer by default)
  const active = getActiveBlock();
  if (!active && document.getElementById('drukcontainer')) {
    document.getElementById('drukcontainer').style.display = 'block';
  }

  // Optional: mark the corresponding pill active on load
  const visibleId = getActiveBlock()?.id;
  if (visibleId) {
    const pill = categoryList?.querySelector(`.a2-pill[data-target="${visibleId}"]`);
    if (pill) pill.classList.add('active');
  }

  convert();
});
