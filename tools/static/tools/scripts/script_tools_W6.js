// Tool W6: Vermogen, energie & kosten
// Geüpdatet met Europese duizendtallen (punt) formatting

// --- Configuraties ---
const properties = {
  water:      { rho: 998,    cp: 4.1868 },
  air:        { rho: 1.225,  cp: 1.005  },
  'prop30%':  { rho: 1030,   cp: 3.60   },
};

const sliderConfigs = {
  water:    { slider1: { min: 0,     max: 20,     step: 0.1 }},
  air:      { slider1: { min: 0,     max: 100000, step: 100   } },
  'prop30%':{ slider1: { min: 0,     max: 5,      step: 0.1 } },
};

const debietConfigs = {
  literpersecond:     { min: 0,      max: 20,        step: 0.1   },
  kuubperhour:         { min: 0,     max: 100000,   step: 1     },
  kilogrampersecond: { min: 0,       max: 2,     step: 0.01     },
};

const timeConfigs = {
  uur:     { min: 0,      max: 8760,        step: 0.1   },
  minuut:  { min: 0,      max: 60,   step: 1     },
  seconde: { min: 0,      max: 60, step: 1     },
};

// map van slider-id naar input-id
const sliderToInput = {
  slider1: 'slider-value1',
  slider2: 'slider-value2',
  slider3: 'slider-value3',
  slider4: 'slider-value4'
};

// --- Helpers ---
function toKgPerS(raw, unit, medium) {
  const { rho } = properties[medium] || properties.water;
  let volM3s;
  switch (unit) {
    case 'literpersecond':   volM3s = raw * 1e-3;        break;
    case 'kuubperhour':  volM3s = raw / 3600;        break;
    case 'literperminute': volM3s = raw * (1/1000) / 60; break;
    case 'kilogrampersecond':  return raw;
    default:      volM3s = raw * 1e-3;
  }
  return volM3s * rho;
}

function calculate(rawFlow, deltaT, hours, price, flowUnit, medium) {
  const { cp } = properties[medium] || properties.water;
  const mDot = toKgPerS(rawFlow, flowUnit, medium);
  const powerKw = mDot * deltaT * cp;      // kJ/s = kW
  const energyKwh = powerKw * hours;
  const cost = energyKwh * price;
  return { mDot, powerKw, energyKwh, cost };
}

function applyConfig(sliderId, cfg) {
  const slider = document.getElementById(sliderId);
  const input  = document.getElementById(sliderToInput[sliderId]);
  if (!slider || !input) return;
  slider.min  = cfg.min;
  slider.max  = cfg.max;
  slider.step = cfg.step;
  let val = parseFloat(slider.value);
  if (val < cfg.min) val = cfg.min;
  if (val > cfg.max) val = cfg.max;
  slider.value = input.value = val;
}

// --- Core update functie ---
function updateValues() {
  const rawFlow  = parseFloat(document.getElementById('slider1').value);
  const deltaT   = parseFloat(document.getElementById('slider2').value);
  const rawTime  = parseFloat(document.getElementById('slider3').value);
  const price    = parseFloat(document.getElementById('slider4').value);
  const flowUnit = document.getElementById('unit_debiet').value;
  const medium   = document.getElementById('medium').value;
  const timeUnit = document.getElementById('unit_time').value;

  // converteer naar uren
  let hours;
  if (timeUnit === 'minuut')  hours = rawTime / 60;
  else if (timeUnit === 'seconde') hours = rawTime / 3600;
  else hours = rawTime;

  const { powerKw, energyKwh, cost } = calculate(
    rawFlow, deltaT, hours, price, flowUnit, medium
  );

  // update DOM met Europese duizendtallen
  document.getElementById('dichtheid').textContent     = properties[medium]?.rho.toLocaleString('nl-NL', { minimumFractionDigits: 2, maximumFractionDigits:2 });
  document.getElementById('specific_heat').textContent = properties[medium]?.cp.toLocaleString('nl-NL', { minimumFractionDigits: 2, maximumFractionDigits:2 });
  document.getElementById('powerkW').textContent       = powerKw.toLocaleString('nl-NL', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
  document.getElementById('powerW').textContent        = (powerKw * 1000).toLocaleString('nl-NL', { minimumFractionDigits:0, maximumFractionDigits:0 });
  document.getElementById('energykWh').textContent     = energyKwh.toLocaleString('nl-NL', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
  document.getElementById('energyMJ').textContent      = (energyKwh * 3.6).toLocaleString('nl-NL', { minimumFractionDigits:0, maximumFractionDigits:0 });
  document.getElementById('euros').textContent         = cost.toLocaleString('nl-NL', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

// --- Initialisatie ---
function init() {
  // sync slider <-> input
  Object.entries(sliderToInput).forEach(([sliderId, inputId]) => {
    const slider = document.getElementById(sliderId);
    const input  = document.getElementById(inputId);
    slider.addEventListener('input', () => {
      input.value = slider.value;
      updateValues();
    });
    input.addEventListener('input', () => {
      let val = parseFloat(input.value);
      if (isNaN(val)) return;
      val = Math.min(Math.max(val, +slider.min), +slider.max);
      slider.value = input.value = val;
      updateValues();
    });
  });

  // dropdown listeners
  document.getElementById('medium').addEventListener('change', () => {
    const med = document.getElementById('medium').value;

    const unitSelect = document.getElementById('unit_debiet');
    if (med === 'water') unitSelect.value = 'literpersecond';
    else if (med === 'air') unitSelect.value = 'kuubperhour';
    updateValues();
  });

    // bij unit_debiet-change: pas slider1 range aan
  document.getElementById('unit_debiet').addEventListener('change', () => {
    const cfg = debietConfigs[document.getElementById('unit_debiet').value] || debietConfigs.kuubperhour;
    applyConfig('slider1', cfg);
    updateValues();
  });

  // bij unit_time-change: pas slider3 range aan
  document.getElementById('unit_time').addEventListener('change', () => {
    const cfg = timeConfigs[document.getElementById('unit_time').value] || timeConfigs.uur;
    applyConfig('slider3', cfg);
    updateValues();
  });


  // prijs slider
  document.getElementById('slider4').addEventListener('input', updateValues);

  // buttons
  document.getElementById('printButton').addEventListener('click', () => window.print());
  document.getElementById('readMeButton').addEventListener('click', () => window.open(pdfUrlReadMe, '_blank'));
  document.getElementById('excelButton').addEventListener('click', () => window.open(pdfUrlExcel, '_blank'));

  // kickstart
  updateValues();
}

document.addEventListener('DOMContentLoaded', init);
