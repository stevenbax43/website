(() => {
  // avoid double wiring if the script is included twice
  if (window.__bufferInit) return;
  window.__bufferInit = true;

  // ===== Save / Load =====
  function saveInputValues() {
    const fields = document.querySelectorAll('input[type="number"], input[type="text"], select');
    fields.forEach(field => {
      const { id, type, name, value } = field;
      if (id && type !== 'hidden' && name !== 'csrfmiddlewaretoken') {
        sessionStorage.setItem(id, value);
      }
    });
  }

  function loadInputValues() {
    const fields = document.querySelectorAll('input[type="number"], input[type="text"], select');
    fields.forEach(field => {
      const { id, type, name } = field;
      if (id && type !== 'hidden' && name !== 'csrfmiddlewaretoken') {
        const savedValue = sessionStorage.getItem(id);
        if (savedValue !== null) field.value = savedValue;
      }
    });
  }

  // ===== Auto-trigger control (no reload loops) =====
  const HREF = location.href.split('#')[0];
  const KEY_ARM = `Buffer:armed:${location.pathname}`;
  let leavingToDifferent = false;

  function submitNow() {
    saveInputValues();
    const form = document.getElementById('inputForm');
    if (form?.requestSubmit) form.requestSubmit();
    else if (form) form.submit();
    else document.getElementById('calculateButton')?.click();
  }

  function triggerOncePerVisit() {
    sessionStorage.setItem(KEY_ARM, '1'); // mark first to avoid re-entrancy
    submitNow();
    console.log('[Buffer] auto-triggered');
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
      console.log('[Buffer] skipped auto-trigger');
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
  });

  // ===== DOMContentLoaded: wire UI (no auto-trigger here) =====
  document.addEventListener('DOMContentLoaded', function () {
    // Load input values
    loadInputValues();

    // Save & submit on change
    document.querySelectorAll('input[type="number"], input[type="text"], select').forEach(field => {
      field.addEventListener('change', function () {
        saveInputValues();
        const form = document.getElementById('inputForm');
        if (form?.requestSubmit) form.requestSubmit();
        else if (form) form.submit();
        else document.getElementById('calculateButton')?.click();
      });
    });

    // Buttons (guarded)
    document.getElementById('printButton')?.addEventListener('click', () => window.print());
    
    document.getElementById('excelButton')?.addEventListener('click', () => window.open(pdfUrlExcel, '_blank'));
  });
})();