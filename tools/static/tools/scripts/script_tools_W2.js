//https://flamco.aalberts-hfc.com/media/files/calculationtools/ins.vls.flexcon-calculation-page_1.pdf

(() => {
  // avoid double wiring
  if (window.__expansieInit) return;
  window.__expansieInit = true;

  // ===== Save / Load =====
  function saveInputValues() {
    document.querySelectorAll('input, select').forEach(field => {
      if (field.type !== 'hidden' && field.name !== 'csrfmiddlewaretoken' && field.id) {
        sessionStorage.setItem(field.id, field.value);
      }
    });
    const locToggle = document.getElementById('locatieToggle');
    if (locToggle) sessionStorage.setItem('locatieToggle', String(locToggle.checked));
  }

  function loadInputValues() {
    document.querySelectorAll('input, select').forEach(field => {
      if (field.type !== 'hidden' && field.name !== 'csrfmiddlewaretoken' && field.id) {
        const saved = sessionStorage.getItem(field.id);
        if (saved !== null) field.value = saved;
      }
    });
    const locToggle = document.getElementById('locatieToggle');
    if (locToggle) locToggle.checked = sessionStorage.getItem('locatieToggle') === 'true';
  }

  // ===== Toggle “additional fields” =====
  function toggleAdditionalFields(isExpanded) {
    const additional = document.getElementById('additional_fields');
    const toggleButton = document.getElementById('toggleButton');
    if (!toggleButton) return;

    if (additional) {
      additional.classList.toggle('show', !!isExpanded);
    }
    toggleButton.setAttribute('aria-expanded', String(!!isExpanded));
    const icon = toggleButton.querySelector('i');
    if (icon) {
      icon.classList.toggle('fa-chevron-down', !isExpanded);
      icon.classList.toggle('fa-chevron-up', isExpanded);
    }
    toggleButton.innerHTML = `<i class="fas ${isExpanded ? 'fa-chevron-up' : 'fa-chevron-down'}"></i> ${isExpanded ? 'Inklappen' : 'Uitbreiden'}`;
    sessionStorage.setItem('additionalFieldsExpanded', String(!!isExpanded));
  }

  // ===== Auto-trigger control (no reload loops) =====
  const HREF = location.href.split('#')[0];
  const KEY_ARM = `Expansie:armed:${location.pathname}`;
  let leavingToDifferent = false;

  function submitNow() {
    saveInputValues();
    const form = document.getElementById('inputForm');
    if (form?.requestSubmit) form.requestSubmit();
    else if (form) form.submit();
    else document.getElementById('ExpansieButton')?.click();
  }

  function triggerOncePerVisit() {
    sessionStorage.setItem(KEY_ARM, '1'); // mark first to avoid re-entrancy
    submitNow();
    console.log('[Expansie] auto-triggered');
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
      console.log('[Expansie] skipped auto-trigger');
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

  // Disarm only for BFCache or different-page navigations (not reloads)
  window.addEventListener('pagehide', (e) => {
    if (e.persisted || leavingToDifferent) {
      sessionStorage.removeItem(KEY_ARM);
    }
  });

  // ===== DOMContentLoaded: wire UI (no auto-trigger here) =====
  document.addEventListener('DOMContentLoaded', function () {
    // load values
    loadInputValues();

    // additional fields initial state + toggle button
    const storedState = sessionStorage.getItem('additionalFieldsExpanded');
    const isExpanded = storedState === 'true';
    if (document.getElementById('toggleButton')) {
      toggleAdditionalFields(isExpanded);
      document.getElementById('toggleButton')?.addEventListener('click', function () {
        const current = this.getAttribute('aria-expanded') === 'true';
        toggleAdditionalFields(!current);
      });
    }

    // Save & submit on change (single listener per field)
    document.querySelectorAll('input, select').forEach(field => {
      field.addEventListener('change', function () {
        saveInputValues();
        // submit/click
        const form = document.getElementById('inputForm');
        if (form?.requestSubmit) form.requestSubmit();
        else if (form) form.submit();
        else document.getElementById('ExpansieButton')?.click();
      });
    });

    // Buttons (guarded)
    document.getElementById('printButton')?.addEventListener('click', () => window.print());

    document.getElementById('excelButton')?.addEventListener('click', () => window.open(pdfUrlExcel, '_blank'));
  });
})();