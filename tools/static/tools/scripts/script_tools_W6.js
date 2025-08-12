(() => {
  // prevent double wiring
  if (window.__w6Init) return;
  window.__w6Init = true;

  // ================== Your existing config ==================
  const properties = {
    water:      { rho: 998,    cp: 4.1868 },
    air:        { rho: 1.225,  cp: 1.005  },
    'prop30%':  { rho: 1030,   cp: 3.60   },
  };

  const sliderConfigs = {
    water:    { slider1: { min: 0,     max: 20,     step: 0.1 } },
    air:      { slider1: { min: 0,     max: 100000, step: 100 } },
    'prop30%':{ slider1: { min: 0,     max: 5,      step: 0.1 } },
  };

  const debietConfigs = {
    literpersecond:     { min: 0,   max: 20,     step: 0.1  },
    kuubperhour:        { min: 0,   max: 100000, step: 1    },
    kilogrampersecond:  { min: 0,   max: 2,      step: 0.01 },
  };

  const timeConfigs = {
    uur:     { min: 0, max: 8760, step: 0.1 },
    minuut:  { min: 0, max: 60,   step: 1   },
    seconde: { min: 0, max: 60,   step: 1   },
  };

  const sliderToInput = {
    slider1: 'slider-value1',
    slider2: 'slider-value2',
    slider3: 'slider-value3',
    slider4: 'slider-value4'
  };

  // ================== Helpers ==================
  const KEY = (id) => `W6:${location.pathname}:${id}`;
  const KEY_ARM = `W6:armed:${location.pathname}`;
  const KEY_SCROLL = `W6:scroll:${location.pathname}`;
  let leavingToDifferent = false;

  function toKgPerS(raw, unit, medium) {
    const { rho } = properties[medium] || properties.water;
    let volM3s;
    switch (unit) {
      case 'literpersecond':      volM3s = raw * 1e-3;       break;
      case 'kuubperhour':         volM3s = raw / 3600;       break;
      case 'kilogrampersecond':   return raw;
      // (optional) literperminute support:
      case 'literperminute':      volM3s = (raw / 1000) / 60; break;
      default:                    volM3s = raw * 1e-3;
    }
    return volM3s * rho;
  }

  function calculate(rawFlow, deltaT, hours, price, flowUnit, medium) {
    const { cp } = properties[medium] || properties.water;
    const mDot = toKgPerS(rawFlow, flowUnit, medium);
    const powerKw = mDot * deltaT * cp; // kJ/s == kW
    const energyKwh = powerKw * hours;
    const cost = energyKwh * price;
    return { mDot, powerKw, energyKwh, cost };
  }

  function applyConfig(sliderId, cfg) {
    const slider = document.getElementById(sliderId);
    const input  = document.getElementById(sliderToInput[sliderId]);
    if (!slider || !input || !cfg) return;
    slider.min  = cfg.min;
    slider.max  = cfg.max;
    slider.step = cfg.step;
    let val = parseFloat(slider.value);
    if (isNaN(val)) val = +cfg.min;
    if (val < cfg.min) val = cfg.min;
    if (val > cfg.max) val = cfg.max;
    slider.value = input.value = val;
  }

  // ================== Save / Load ==================
  function saveInputValues() {
    document.querySelectorAll('input, select').forEach(field => {
      if (!field.id) return;
      if (field.type === 'hidden' || field.name === 'csrfmiddlewaretoken') return;
      const value = field.type === 'checkbox' ? String(field.checked) : field.value;
      sessionStorage.setItem(KEY(field.id), value);
    });
  }

  function loadInputValues() {
    document.querySelectorAll('input, select').forEach(field => {
      if (!field.id) return;
      if (field.type === 'hidden' || field.name === 'csrfmiddlewaretoken') return;
      const saved = sessionStorage.getItem(KEY(field.id));
      if (saved == null) return;
      if (field.type === 'checkbox') field.checked = (saved === 'true');
      else field.value = saved;
    });
  }

  // ================== Core update ==================
  function updateValues() {
    const rawFlow  = parseFloat(document.getElementById('slider1').value);
    const deltaT   = parseFloat(document.getElementById('slider2').value);
    const rawTime  = parseFloat(document.getElementById('slider3').value);
    const price    = parseFloat(document.getElementById('slider4').value);
    const flowUnit = document.getElementById('unit_debiet').value;
    const medium   = document.getElementById('medium').value;
    const timeUnit = document.getElementById('unit_time').value;

    let hours = rawTime;
    if (timeUnit === 'minuut') hours = rawTime / 60;
    else if (timeUnit === 'seconde') hours = rawTime / 3600;

    const { powerKw, energyKwh, cost } = calculate(rawFlow, deltaT, hours, price, flowUnit, medium);

    document.getElementById('dichtheid').textContent     = properties[medium]?.rho.toLocaleString('nl-NL', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    document.getElementById('specific_heat').textContent = properties[medium]?.cp.toLocaleString('nl-NL', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    document.getElementById('powerkW').textContent       = powerKw.toLocaleString('nl-NL', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
    document.getElementById('powerW').textContent        = (powerKw * 1000).toLocaleString('nl-NL', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
    document.getElementById('energykWh').textContent     = energyKwh.toLocaleString('nl-NL', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
    document.getElementById('energyMJ').textContent      = (energyKwh * 3.6).toLocaleString('nl-NL', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
    document.getElementById('euros').textContent         = cost.toLocaleString('nl-NL', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
  }

  // ================== Init (wire UI) ==================
  function initUI() {
    // sync slider <-> input
    Object.entries(sliderToInput).forEach(([sliderId, inputId]) => {
      const slider = document.getElementById(sliderId);
      const input  = document.getElementById(inputId);
      if (!slider || !input) return;

      slider.addEventListener('input', () => {
        input.value = slider.value;
        saveInputValues();
        updateValues();
      });

      input.addEventListener('input', () => {
        let val = parseFloat(input.value);
        if (isNaN(val)) return;
        val = Math.min(Math.max(val, +slider.min), +slider.max);
        slider.value = input.value = val;
        saveInputValues();
        updateValues();
      });
    });

    // dropdown listeners
    document.getElementById('medium')?.addEventListener('change', () => {
      const med = document.getElementById('medium').value;
      // optional: when medium changes, choose a sensible default unit
      const unitSelect = document.getElementById('unit_debiet');
      if (unitSelect) {
        if (med === 'water') unitSelect.value = 'literpersecond';
        else if (med === 'air') unitSelect.value = 'kuubperhour';
      }
      saveInputValues();
      updateValues();
    });

    document.getElementById('unit_debiet')?.addEventListener('change', () => {
      const cfg = debietConfigs[document.getElementById('unit_debiet').value] || debietConfigs.kuubperhour;
      applyConfig('slider1', cfg);
      saveInputValues();
      updateValues();
    });

    document.getElementById('unit_time')?.addEventListener('change', () => {
      const cfg = timeConfigs[document.getElementById('unit_time').value] || timeConfigs.uur;
      applyConfig('slider3', cfg);
      saveInputValues();
      updateValues();
    });

    // price slider direct
    document.getElementById('slider4')?.addEventListener('input', () => {
      saveInputValues();
      updateValues();
    });

    // buttons
    document.getElementById('printButton')?.addEventListener('click', () => window.print());
    document.getElementById('excelButton')?.addEventListener('click', () => window.open(pdfUrlExcel, '_blank'));
    // Optional: README wrapper for W6 (works only if this is inline template JS)
    document.getElementById('readMeButton')?.addEventListener('click', (e) => {
      e.preventDefault();
      window.open("{% url 'tools:tool-readme' 'W6' %}", "_blank");
    });

    // scroll memory
    const pos = sessionStorage.getItem(KEY_SCROLL);
    if (pos) window.scrollTo(0, parseInt(pos, 10));
    window.addEventListener('scroll', () => {
      sessionStorage.setItem(KEY_SCROLL, String(window.scrollY));
    });
  }

  // ================== Auto-trigger control ==================
  const HREF = location.href.split('#')[0];

  function navType() {
    const nav = performance.getEntriesByType?.('navigation')?.[0];
    return nav?.type; // 'navigate' | 'reload' | 'back_forward'
  }

  function shouldTrigger(e) {
    const type = navType();
    const armed = sessionStorage.getItem(KEY_ARM) === '1';
    const sameUrlRef = (document.referrer || '').split('#')[0] === HREF;

    if (e?.persisted || type === 'back_forward') return true; // Back/Forward return
    if (type === 'reload') return false;                       // avoid reload loops
    return !armed && !sameUrlRef;                              // first arrival from another page
  }

  function triggerOncePerVisit() {
    sessionStorage.setItem(KEY_ARM, '1'); // mark first
    // After load/restore, ensure configs match saved selections, then update.
    const unitFlow = document.getElementById('unit_debiet')?.value;
    const unitTime = document.getElementById('unit_time')?.value;
    if (unitFlow) applyConfig('slider1', debietConfigs[unitFlow] || debietConfigs.kuubperhour);
    if (unitTime) applyConfig('slider3', timeConfigs[unitTime] || timeConfigs.uur);
    updateValues();
    console.log('[W6] auto-triggered');
  }

  function onPageShow(e) {
    if (shouldTrigger(e)) {
      requestAnimationFrame(() => setTimeout(triggerOncePerVisit, 0));
    } else {
      console.log('[W6] skipped auto-trigger');
    }
  }

  // Detect leaving to a different URL
  function normalize(u) { return new URL(u, location.href).href.split('#')[0]; }
  document.addEventListener('click', (evt) => {
    const a = evt.target.closest?.('a[href]');
    if (a) leavingToDifferent = normalize(a.href) !== HREF;
  });
  document.addEventListener('submit', (evt) => {
    const action = evt.target.getAttribute('action') || location.href;
    leavingToDifferent = normalize(action) !== HREF;
  });

  // Disarm only for BFCache or different-page navigations (not reload)
  window.addEventListener('pagehide', (e) => {
    if (e.persisted || leavingToDifferent) {
      sessionStorage.removeItem(KEY_ARM);
    }
    sessionStorage.setItem(KEY_SCROLL, String(window.scrollY));
  });

  // ================== Boot ==================
  document.addEventListener('DOMContentLoaded', () => {
    // 1) load saved values before wiring configs
    loadInputValues();

    // 2) apply slider ranges to match loaded selections
    const unitFlow = document.getElementById('unit_debiet')?.value;
    const unitTime = document.getElementById('unit_time')?.value;
    if (unitFlow) applyConfig('slider1', debietConfigs[unitFlow] || debietConfigs.kuubperhour);
    if (unitTime) applyConfig('slider3', timeConfigs[unitTime] || timeConfigs.uur);

    // 3) wire UI listeners
    initUI();
  });

  // trigger on initial load & BFCache restores
  window.addEventListener('pageshow', onPageShow);
  // Fallback if script loads after pageshow
  if (document.readyState === 'complete') {
    setTimeout(() => onPageShow({ persisted: false }), 0);
  } else {
    window.addEventListener('load', () => onPageShow({ persisted: false }), { once: true });
  }
})();