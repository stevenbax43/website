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

  function validateTemperature() {
    const startTempInput = document.getElementById('starttemp');
    const eindTempInput  = document.getElementById('eindtemp');
    const tempMessage    = document.getElementById('tempMessage');
    if (!startTempInput || !eindTempInput || !tempMessage) return;

    const startTemp = parseFloat(startTempInput.value);
    const eindTemp  = parseFloat(eindTempInput.value);
    tempMessage.style.display = (isFinite(startTemp) && isFinite(eindTemp) && eindTemp <= startTemp) ? 'block' : 'none';
  }

  function validateTime() {
    const startUurInput = document.getElementById('startuur');
    const eindUurInput  = document.getElementById('einduur');
    const timeMessage   = document.getElementById('timeMessage');
    if (!startUurInput || !eindUurInput || !timeMessage) return;

    const startUur = parseInt(startUurInput.value, 10);
    const eindUur  = parseInt(eindUurInput.value, 10);
    timeMessage.style.display = (isFinite(startUur) && isFinite(eindUur) && startUur >= eindUur) ? 'block' : 'none';
  }

  // ================== Auto-trigger control (no reload loops) ==================
  const HREF = location.href.split('#')[0];
  const KEY_ARM   = `Klimaat:armed:${location.pathname}`;
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
      console.log('[Klimaat] skipped auto-trigger');
    }
  }

  // Fire on initial load and BFCache restores
  window.addEventListener('pageshow', onPageShow);
  // Fallback if script loaded after pageshow
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
    // persist final scroll on exit too
    sessionStorage.setItem(KEY_SCROLL, String(window.scrollY));
  });

  // ================== DOMContentLoaded: wire UI (no auto-trigger here) ==================
  document.addEventListener('DOMContentLoaded', function () {
    // Load inputs + derived UI
    loadInputValues();
    updateMaxValue();
    validateTemperature();
    validateTime();

    // Save & submit on change
    const idsAffectingMax = new Set(['HeatBuildingMax','CoolBuildingMax','LimitHeatMax','LimitCoolMax']);
    document.querySelectorAll('input, select').forEach(field => {
      field.addEventListener('change', function () {
        saveInputValues();
        if (idsAffectingMax.has(field.id)) updateMaxValue();
        const form = document.getElementById('inputForm');
        if (form?.requestSubmit) form.requestSubmit();
        else if (form) form.submit();
        else document.getElementById('bedrijfsurenknop')?.click();
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
    

    document.getElementById('printButton')?.addEventListener('click', () => window.print());
    document.getElementById('excelButton')?.addEventListener('click', () => {
      fetch(downloadExcelUrl)
        .then(r => r.blob())
        .then(blob => {
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = 'Klimaatjaar_2018.xlsx';
          link.click();
          window.URL.revokeObjectURL(url);
        });
    });

    // Optional: buttons that intentionally reload
    document.querySelectorAll('.save-and-reload').forEach(button => {
      button.addEventListener('click', (event) => {
        event.preventDefault();
        saveInputValues();
        location.reload(); // note: reloads do NOT auto-trigger (by design)
      });
    });
  });
})();