(() => {
  // avoid double wiring
  if (window.__klimaatInit) return;
  window.__klimaatInit = true;

  // ================== Save / Load ==================
  function saveInputValues() {
    document.querySelectorAll('input, select').forEach(field => {
      if (field.type !== 'hidden' && field.name !== 'csrfmiddlewaretoken' && field.id) {
        sessionStorage.setItem(field.id, field.value);
      }
    });
  }

  function loadInputValues() {
    document.querySelectorAll('input, select').forEach(field => {
      if (field.type !== 'hidden' && field.name !== 'csrfmiddlewaretoken' && field.id) {
        const saved = sessionStorage.getItem(field.id);
        if (saved !== null) field.value = saved;
      }
    });
  }

  // ================== Page-specific helpers ==================
  function updateMaxValue() {
    const HeatBuildingMax = document.getElementById("HeatBuildingMax");
    const LimitHeatMax    = document.getElementById("LimitHeatMax");
    const CoolBuildingMax = document.getElementById("CoolBuildingMax");
    const LimitCoolMax    = document.getElementById("LimitCoolMax");
    const LimitHeatMin    = document.getElementById("LimitHeatMin");
    const LimitCoolMin    = document.getElementById("LimitCoolMin");

    if (HeatBuildingMax && LimitHeatMax) LimitHeatMax.max = HeatBuildingMax.value;
    if (CoolBuildingMax && LimitCoolMax) LimitCoolMax.max = CoolBuildingMax.value;
    if (LimitHeatMin && LimitHeatMax)    LimitHeatMin.max = LimitHeatMax.value;
    if (LimitCoolMin && LimitCoolMax)    LimitCoolMin.max = LimitCoolMax.value;
  }
  // If your HTML still has inline oninput="updateMaxValue()", expose it:
  window.updateMaxValue = updateMaxValue;

  function validateTemperature() {
    const startTempInput = document.getElementById('starttemp');
    const eindTempInput  = document.getElementById('eindtemp');
    const tempMessage    = document.getElementById('tempMessage');
    if (!startTempInput || !eindTempInput || !tempMessage) return;

    const startTemp = parseFloat(startTempInput.value);
    const eindTemp  = parseFloat(eindTempInput.value);
    const show = (isFinite(startTemp) && isFinite(eindTemp) && eindTemp <= startTemp);
    // Toggle Bootstrap d-none instead of style.display
    tempMessage.classList.toggle('d-none', !show);
  }

  function validateTime() {
    const startUurInput = document.getElementById('startuur');
    const eindUurInput  = document.getElementById('einduur');
    const timeMessage   = document.getElementById('timeMessage');
    if (!startUurInput || !eindUurInput || !timeMessage) return;

    const startUur = parseInt(startUurInput.value, 10);
    const eindUur  = parseInt(eindUurInput.value, 10);
    const show = (isFinite(startUur) && isFinite(eindUur) && startUur >= eindUur);
    timeMessage.classList.toggle('d-none', !show);
  }

  // ================== Helpers for Save PDF ==================
  function getCsrfToken() {
    // Prefer the hidden input in the form
    const input = document.querySelector('form#inputForm input[name="csrfmiddlewaretoken"]');
    if (input) return input.value;
    // Fallback to cookie
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? m[1] : '';
  }

  function canvasToPNG(id) {
    const el = document.getElementById(id);
    if (!el || el.tagName.toLowerCase() !== 'canvas') return null;
    try {
      return el.toDataURL('image/png'); // data:image/png;base64,....
    } catch (e) {
      console.error('Canvas export failed for', id, e);
      return null;
    }
  }

  function selectedText(selectId) {
    const el = document.getElementById(selectId);
    if (!el) return '';
    const opt = el.selectedOptions && el.selectedOptions[0];
    return opt ? opt.text : el.value || '';
  }

  function valueOf(id) {
    const el = document.getElementById(id);
    if (!el) return '';
    // support <output> and normal inputs
    if (el.tagName.toLowerCase() === 'output') return el.textContent.trim();
    return el.value ?? '';
  }

  async function postForPdf(btn) {
    const url = btn?.dataset?.pdfUrl;
    if (!url) throw new Error('PDF URL ontbreekt (data-pdf-url).');

    const fd  = new FormData();

    // Important: to pass the guard in the Django view
    fd.append('SavePDFButton', '1');

    // meta
    const pageTitle = document.querySelector('.tools-hero h1')?.textContent?.trim() || 'Tool A3: Klimaatjaar';
    fd.append('project_title', pageTitle);

    // bedrijfsuren & method (send both value and label text)
    fd.append('method', valueOf('method'));
    fd.append('method_text', selectedText('method'));

    fd.append('startdag', valueOf('startdag'));
    fd.append('startdag_text', selectedText('startdag'));
    fd.append('startuur', valueOf('startuur'));

    fd.append('einddag', valueOf('einddag'));
    fd.append('einddag_text', selectedText('einddag'));
    fd.append('einduur', valueOf('einduur'));

    // buiten temp grens
    fd.append('starttemp', valueOf('starttemp'));
    fd.append('eindtemp', valueOf('eindtemp'));

    // verwarming
    fd.append('HeatBuildingMax', valueOf('HeatBuildingMax'));
    fd.append('HeatBuildingMin', valueOf('HeatBuildingMin'));
    fd.append('maxTempHeat', valueOf('maxTempHeat'));
    fd.append('designTempheat', valueOf('designTempheat'));

    // koeling
    fd.append('CoolBuildingMax', valueOf('CoolBuildingMax'));
    fd.append('CoolBuildingMin', valueOf('CoolBuildingMin'));
    fd.append('maxTempCool', valueOf('maxTempCool'));
    fd.append('designTempcool', valueOf('designTempcool'));

    // grenzen & factors
    fd.append('LimitHeatMax', valueOf('LimitHeatMax'));
    fd.append('LimitHeatMin', valueOf('LimitHeatMin'));
    fd.append('LimitCoolMax', valueOf('LimitCoolMax'));
    fd.append('LimitCoolMin', valueOf('LimitCoolMin'));

    fd.append('B_factor_heat', valueOf('B_factor_heat'));
    fd.append('E_factor_heat', valueOf('E_factor_heat'));
    fd.append('B_factor_cool', valueOf('B_factor_cool'));
    fd.append('E_factor_cool', valueOf('E_factor_cool'));

    fd.append('on_hours', valueOf('on_hours'));
    fd.append('off_hours', valueOf('off_hours'));
    fd.append('username', valueOf('username'));
  
    // canvases -> data URLs
    const chartMap = {
      'myDoughnutChart':     'chart_myDoughnutChart',
      'myOnOffChart':        'chart_myOnOffChart',
      'myLineChart':         'chart_myLineChart',
      'myBarChart_heat':     'chart_myBarChart_heat',
      'myBarChart_cool':     'chart_myBarChart_cool',
      'belastingduurcurve':  'chart_belastingduurcurve'
    };
    Object.entries(chartMap).forEach(([domId, field]) => {
      const png = canvasToPNG(domId);
      if (png) fd.append(field, png);
    });

    const resp = await fetch(url, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken() },
      body: fd
    });
    if (!resp.ok) {
      const t = await resp.text();
      throw new Error(t || 'PDF genereren mislukt');
    }
    const blob = await resp.blob();
    const a = document.createElement('a');
    const href = URL.createObjectURL(blob);
    a.href = href;
    a.download = 'tool_A3_klimaatjaar.pdf';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(href);
  }

  // ================== Auto-trigger control (no reload loops) ==================
  const HREF = location.href.split('#')[0];
  const KEY_ARM    = `Klimaat:armed:${location.pathname}`;
  const KEY_SCROLL = `scrollPosition:${location.pathname}`;
  let leavingToDifferent = false;

  function submitNow() {
    saveInputValues();
    const form = document.getElementById('inputForm');
    if (form?.requestSubmit) form.requestSubmit();
    else if (form) form.submit();
    else document.getElementById('bedrijfsurenknop')?.click();
  }

  function triggerOncePerVisit() {
    sessionStorage.setItem(KEY_ARM, '1'); // mark first to avoid re-entrancy
    submitNow();
    console.log('[Klimaat] auto-triggered');
  }

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

  function onPageShow(e) {
    if (shouldTrigger(e)) {
      requestAnimationFrame(() => setTimeout(triggerOncePerVisit, 0));
    } else {
      // no-op
    }
  }

  // Fire on initial load and BFCache restores
  window.addEventListener('pageshow', onPageShow);
  if (document.readyState === 'complete') {
    setTimeout(() => onPageShow({ persisted: false }), 0);
  } else {
    window.addEventListener('load', () => onPageShow({ persisted: false }), { once: true });
  }

  // Detect leaving to a different URL (so Back should re-trigger)
  function normalize(u) { return new URL(u, location.href).href.split('#')[0]; }
  document.addEventListener('click', (e) => {
    const a = e.target.closest?.('a[href]');
    if (a) leavingToDifferent = normalize(a.href) !== HREF;
  });
  document.addEventListener('submit', (e) => {
    const action = e.target.getAttribute('action') || location.href;
    leavingToDifferent = normalize(action) !== HREF;
  });

  // Disarm only when going into BFCache or to a different page (not reload)
  window.addEventListener('pagehide', (e) => {
    if (e.persisted || leavingToDifferent) {
      sessionStorage.removeItem(KEY_ARM);
    }
    sessionStorage.setItem(KEY_SCROLL, String(window.scrollY));
  });

  // ================== DOMContentLoaded: wire UI ==================
  document.addEventListener('DOMContentLoaded', function () {
    // Load inputs + derived UI
    loadInputValues();
    updateMaxValue();
    validateTemperature();
    validateTime();

    // Save & submit on change, and update maxima live while typing
    const idsAffectingMax = new Set(['HeatBuildingMax','CoolBuildingMax','LimitHeatMax','LimitCoolMax','LimitHeatMin','LimitCoolMin']);

    document.querySelectorAll('input, select').forEach(field => {
      field.addEventListener('input', () => {
        if (idsAffectingMax.has(field.id)) updateMaxValue();
      });
      field.addEventListener('change', () => {
        saveInputValues();
        if (idsAffectingMax.has(field.id)) updateMaxValue();
        submitNow();
      });
    });

    // Live validation
    document.getElementById('starttemp')?.addEventListener('input', validateTemperature);
    document.getElementById('eindtemp')?.addEventListener('input', validateTemperature);
    document.getElementById('startuur')?.addEventListener('input', validateTime);
    document.getElementById('einduur')?.addEventListener('input', validateTime);

    // Scroll memory (per path)
    const scrollPosition = sessionStorage.getItem(KEY_SCROLL) || sessionStorage.getItem('scrollPosition');
    if (scrollPosition) window.scrollTo(0, parseInt(scrollPosition, 10));
    window.addEventListener('scroll', () => {
      sessionStorage.setItem(KEY_SCROLL, String(window.scrollY));
    });

    // Buttons
    document.getElementById('printButton')?.addEventListener('click', (e) => {
      e.preventDefault();
      window.print();
    });

    document.getElementById('excelButton')?.addEventListener('click', (e) => {
      e.preventDefault();
      const url = (typeof downloadExcelUrl !== 'undefined' && downloadExcelUrl)
        ? downloadExcelUrl
        : e.currentTarget.dataset.url; // fallback if you add data-url on the link
      if (!url) return;
      fetch(url)
        .then(r => r.blob())
        .then(blob => {
          const href = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = href;
          a.download = 'Klimaatjaar_2018.xlsx';
          document.body.appendChild(a);
          a.click();
          a.remove();
          URL.revokeObjectURL(href);
        });
    });

    // SAVE PDF (server-side via ReportLab)
    const savePdfBtn = document.getElementById('SavePDFButton');
    if (savePdfBtn) {
      savePdfBtn.addEventListener('click', (e) => {
        e.preventDefault();
        postForPdf(savePdfBtn).catch(err => {
          console.error(err);
          alert('Kon PDF niet genereren:\n' + (err?.message || err));
        });
      });
    }

    // Optional: buttons that intentionally reload
    document.querySelectorAll('.save-and-reload').forEach(button => {
      button.addEventListener('click', (event) => {
        event.preventDefault();
        saveInputValues();
        location.reload(); // reloads do NOT auto-trigger (by design)
      });
    });
  });
})();
