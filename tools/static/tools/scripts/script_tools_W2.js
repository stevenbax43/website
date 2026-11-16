//https://flamco.aalberts-hfc.com/media/files/calculationtools/ins.vls.flexcon-calculation-page_1.pdf

(() => {
  // avoid double wiring
  if (window.__expansieInit) return;
  window.__expansieInit = true;

  // ===== Save / Load =====
  function saveInputValues() {
    document.querySelectorAll('input, select').forEach(field => {
      if (field.type !== 'hidden' && field.name !== 'csrfmiddlewaretoken' && field.id) {
        const value = field.type === 'checkbox' ? String(field.checked) : field.value;
        sessionStorage.setItem(field.id, value);
      }
    });
  }

  function loadInputValues() {
    document.querySelectorAll('input, select').forEach(field => {
      if (field.type !== 'hidden' && field.name !== 'csrfmiddlewaretoken' && field.id) {
        const saved = sessionStorage.getItem(field.id);
        if (saved !== null) {
          if (field.type === 'checkbox') field.checked = saved === 'true';
          else field.value = saved;
        }
      }
    });
  }

  function updateSystemVolumeMode() {
    const calculationMode = document.getElementById('calculation_mode');
    const isCooling = calculationMode?.value === 'cooling';
    const unknownToggle = document.getElementById('sys_inhoud_onbekend');
    const knownInput = document.getElementById('sys_inhoud');
    const knownInputContainer = document.getElementById('system_volume_input');
    const estimatedFields = document.getElementById('estimated_volume_fields');
    const powerField = document.getElementById('boiler_power_field');
    const cvField = document.getElementById('cv_emission_field');
    const powerInput = document.getElementById('vermogen');
    const cvSelect = document.getElementById('CVInstallatie');
    const unknownToggleContainer = document.getElementById('unknown_volume_switch');
    const heatingTemperatures = document.querySelectorAll('.heating-temperature-field');
    const coolingParameters = document.getElementById('cooling_parameters');
    const heatingNotes = document.querySelectorAll('.heating-only');
    const coolingNotes = document.querySelectorAll('.cooling-only');
    if (!unknownToggle || !knownInput || !knownInputContainer || !estimatedFields ||
        !powerField || !cvField || !powerInput || !cvSelect) return;

    const isUnknown = unknownToggle.checked && !isCooling;
    const minTemp = document.getElementById('cooling_min_temp');
    const maxTemp = document.getElementById('cooling_max_temp');
    const glycol = document.getElementById('glycol_percentage');
    unknownToggle.disabled = isCooling;
    unknownToggleContainer?.classList.toggle('d-none', isCooling);
    heatingTemperatures.forEach(field => field.classList.toggle('d-none', isCooling));
    coolingParameters?.classList.toggle('d-none', !isCooling);
    heatingNotes.forEach(note => note.classList.toggle('d-none', isCooling));
    coolingNotes.forEach(note => note.classList.toggle('d-none', !isCooling));
    knownInputContainer.classList.toggle('d-none', isUnknown);
    estimatedFields.classList.toggle('d-none', !isUnknown);
    powerField.classList.toggle('d-none', !isUnknown);
    cvField.classList.toggle('d-none', !isUnknown);
    knownInput.disabled = isUnknown;
    knownInput.required = !isUnknown;
    powerInput.disabled = !isUnknown;
    powerInput.required = isUnknown;
    cvSelect.disabled = !isUnknown;
    cvSelect.required = isUnknown;
    [minTemp, maxTemp, glycol].forEach(field => {
      if (field) {
        field.disabled = !isCooling;
        field.required = isCooling;
      }
    });
    ['temp_aanvoer', 'temp_retour', 'temp_min'].forEach(id => {
      const field = document.getElementById(id);
      if (field) {
        field.disabled = isCooling;
        field.required = !isCooling;
      }
    });
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

    updateSystemVolumeMode();

    // Save & submit on change (single listener per field)
    const inputForm = document.getElementById('inputForm');
    inputForm?.querySelectorAll('input, select').forEach(field => {
      field.addEventListener('change', function () {
        if (field.id === 'sys_inhoud_onbekend' || field.id === 'calculation_mode') {
          updateSystemVolumeMode();
        }
        saveInputValues();
        if (document.activeElement === document.getElementById('SavePDFButton')) return;
        // submit/click
        if (inputForm?.requestSubmit) inputForm.requestSubmit();
        else if (inputForm) inputForm.submit();
        else document.getElementById('ExpansieButton')?.click();
      });
    });

    // Buttons (guarded)
    document.getElementById('printButton')?.addEventListener('click', () => window.print());

    document.getElementById('excelButton')?.addEventListener('click', () => window.open(pdfUrlExcel, '_blank'));

    document.getElementById('pdfDetailsForm')?.addEventListener('submit', function (event) {
      event.preventDefault();

      const inputForm = document.getElementById('inputForm');
      const pdfButton = document.getElementById('SavePDFButton');
      if (!inputForm || !pdfButton) return;

      const formData = new FormData(inputForm);
      formData.set('project_name', document.getElementById('pdf_project_name').value.trim());
      formData.set('project_number', document.getElementById('pdf_project_number').value.trim());
      formData.set('project_description', document.getElementById('pdf_project_description').value.trim());

      const pdfForm = document.createElement('form');
      pdfForm.method = 'post';
      pdfForm.action = pdfButton.dataset.pdfUrl;
      pdfForm.hidden = true;
      formData.forEach((value, name) => {
        const field = document.createElement('input');
        field.type = 'hidden';
        field.name = name;
        field.value = value;
        pdfForm.appendChild(field);
      });
      document.body.appendChild(pdfForm);
      pdfForm.submit();
      window.setTimeout(() => pdfForm.remove(), 1000);
    });
  });
})();