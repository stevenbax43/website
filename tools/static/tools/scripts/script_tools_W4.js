(() => {
  // prevent double-wiring if the script is included twice
  if (window.__co2Init) return;
  window.__co2Init = true;
  
  // ====== Save/Load (as you had) ==================================================
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
    console.log("LOAD");
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

  // ====== Trigger control ==========================================================
  const HREF = location.href.split('#')[0];
  const KEY_ARM = `CO2:armed:${location.pathname}`;
  const KEY_SCROLL = `scrollPosition:${location.pathname}`;
  let leavingToDifferent = false;

  function submitNow() {
    // Save then submit (prefer requestSubmit)
    saveInputValues();
    const form = document.getElementById('inputForm');
    if (form && typeof form.requestSubmit === 'function') form.requestSubmit();
    else if (form) form.submit();
    else document.getElementById('CO2button')?.click();
  }

  function triggerOncePerVisit() {
    // mark first to avoid re-entrancy
    sessionStorage.setItem(KEY_ARM, '1');
    submitNow();
    console.log('[CO2] auto-triggered');
  }

  function navType() {
    const nav = performance.getEntriesByType?.('navigation')?.[0];
    return nav?.type; // 'navigate' | 'reload' | 'back_forward' | 'prerender'
  }

  function shouldTrigger(e) {
    const type = navType();
    const armed = sessionStorage.getItem(KEY_ARM) === '1';
    const sameUrlRef = (document.referrer || '').split('#')[0] === HREF;

    // Trigger if:
    // - returning via Back/Forward (BFCache), OR
    // - first arrival from a different page (not reload), and we haven't already triggered for this visit
    if (e?.persisted || type === 'back_forward') return true;
    if (type === 'reload') return false;
    return !armed && !sameUrlRef;
  }

  function onPageShow(e) {
    if (shouldTrigger(e)) {
      // wait a tick so DOM is fully ready after restores
      requestAnimationFrame(() => setTimeout(triggerOncePerVisit, 0));
    } else {
      console.log('[CO2] skipped auto-trigger');
    }
  }

  // Fire on initial load and on BFCache restore
  window.addEventListener('pageshow', onPageShow);

  // Fallback: if the script loaded after pageshow on initial load
  if (document.readyState === 'complete') {
    setTimeout(() => onPageShow({ persisted: false }), 0);
  } else {
    window.addEventListener('load', () => onPageShow({ persisted: false }), { once: true });
  }

  // Detect if we’re leaving to a DIFFERENT URL (so Back should re-trigger later)
  function normalize(u) { return new URL(u, location.href).href.split('#')[0]; }

  document.addEventListener('click', (e) => {
    const a = e.target.closest?.('a[href]');
    if (a) {
      const dest = normalize(a.href);
      leavingToDifferent = dest !== HREF;
    }
  });
  //dynamische wissel ventialtie totaal of pp 
  const ventilationMode =
      CO2_data.ventilation_mode || "pp";

  const ventilatiePP =
      CO2_data.ventilatie_pp || 0;

  const ventilatieTotaal =
      CO2_data.ventilatiedebiet_totaal || 0;
  
  // ======================================================
  // Ventilatie
  // ======================================================

  const modeEl =
      document.getElementById("ventilation_mode");

  const labelEl =
      document.getElementById("ventilation_label");

  const unitEl =
      document.getElementById("ventilation_unit");

  const valueEl =
      document.getElementById("ventilation_value");

  const personsEl =
      document.getElementById("number_persons");


  function updateVentilationUI() {

      if (
          !modeEl ||
          !labelEl ||
          !unitEl
      ) return;

      if (modeEl.value === "pp") {

          labelEl.textContent =
              "Debiet per persoon";

          unitEl.textContent =
              "m³/h p.p.";

      } else {

          labelEl.textContent =
              "Totaal ventilatiedebiet";

          unitEl.textContent =
              "m³/h";
      }
  }


  function convertVentilationValue() {

      if (
          !valueEl ||
          !personsEl
      ) return;

      const persons =
          parseFloat(
              personsEl.value || 0
          );

      if (persons <= 0) return;

      let value =
          parseFloat(
              valueEl.value || 0
          );

      if (isNaN(value)) value = 0;

      if (modeEl.value === "pp") {

          // totaal -> pp

          value = value / persons;

      } else {

          // pp -> totaal

          value = value * persons;
      }

      valueEl.value =
          value.toFixed(1);
  }


  modeEl?.addEventListener(
      "change",
      function () {

          convertVentilationValue();

          updateVentilationUI();

          saveInputValues();
      }
  );

  // Resultatenkaarten vullen
   document.addEventListener("DOMContentLoaded", () => {

      const conc =
          document.getElementById(
              "max_concentration_result"
          );

      const increase =
          document.getElementById(
              "max_increase_result"
          );

      const time =
          document.getElementById(
              "time_to_max_result"
          );

      const ventilationResult =
          document.getElementById(
              "ventilation_result"
          );

      const ventilationLabel =
          document.getElementById(
              "ventilation_result_label"
          );

      if (conc) {
          conc.innerHTML =
              `${maxConcentration.toFixed(0)} ppm`;
      }

      if (increase) {
          increase.innerHTML =
              `+${maxIncrease.toFixed(0)} ppm`;
      }

      if (time) {
          time.innerHTML =
              formatHours(maxTimeConcentration);
      }

      if (
          ventilationResult &&
          ventilationLabel
      ) {

          if (ventilationMode === "pp") {

              ventilationResult.innerHTML =
                  `${ventilatieTotaal.toFixed(0)} m³/h`;

              ventilationLabel.innerHTML =
                  "Ventilatiedebiet totaal";

          } else {

              ventilationResult.innerHTML =
                  `${ventilatiePP.toFixed(1)} m³/h.p`;

              ventilationLabel.innerHTML =
                  "Ventilatie per persoon";
          }
      }

  });
  document
  .getElementById("SavePDFButton")
  .addEventListener("click", function () {

      const canvas = document.getElementById("CO2_verloop");

      if (!canvas) return;

      const scale = 4;

      const exportCanvas = document.createElement("canvas");

      exportCanvas.width = canvas.width * scale;
      exportCanvas.height = canvas.height * scale;

      const exportCtx = exportCanvas.getContext("2d");

      exportCtx.fillStyle = "#FFFFFF";
      exportCtx.fillRect(
          0,
          0,
          exportCanvas.width,
          exportCanvas.height
      );

      exportCtx.scale(scale, scale);
      exportCtx.drawImage(canvas, 0, 0);

      const chartImage = exportCanvas
          .toDataURL("image/png")
          .split(",")[1];

      document.getElementById("chart_image_base64").value =
          chartImage;

      document.getElementById("max_concentration").value =
          maxConcentration.toFixed(0);

      document.getElementById("max_increase").value =
          maxIncrease.toFixed(0);

      document.getElementById("time_to_max").value =
          formatHours(maxTimeConcentration);

      const form = document.getElementById("inputForm");

      form.action = this.dataset.pdfUrl;
      form.method = "post";

      form.submit();
  });

  document.addEventListener('submit', (e) => {
    const action = e.target.getAttribute('action') || location.href;
    const dest = normalize(action);
    leavingToDifferent = dest !== HREF;
  });

  // Disarm only when going into BFCache or to a different page (not reload)
  window.addEventListener('pagehide', (e) => {
    if (e.persisted || leavingToDifferent) {
      sessionStorage.removeItem(KEY_ARM);
    }
    // persist final scroll on exit too
    sessionStorage.setItem(KEY_SCROLL, String(window.scrollY));
  });

  // ====== DOMContentLoaded: wire handlers, no auto-trigger here ====================
  document.addEventListener('DOMContentLoaded', function () {
    // Load input values when the page is loaded
    loadInputValues();
    updateVentilationUI();
    // Save & submit on change
    document.querySelectorAll('input').forEach(field => {
      field.addEventListener('change', function () {
        console.log(`[CO2] change -> save+submit: ${field.id}`);
        saveInputValues();
        const form = document.getElementById('inputForm');
        if (form && typeof form.requestSubmit === 'function') form.requestSubmit();
        else if (form) form.submit();
      });
    });

    document.getElementById('production_pp')?.addEventListener('change', function () {
      console.log('[CO2] change -> save+submit: production_pp');
      saveInputValues();
      const form = document.getElementById('inputForm');
      if (form && typeof form.requestSubmit === 'function') form.requestSubmit();
      else if (form) form.submit();
    });

    // Remember and restore scroll position (per path)
    const scrollPosition = sessionStorage.getItem(KEY_SCROLL);
    if (scrollPosition) window.scrollTo(0, parseInt(scrollPosition, 10));
    window.addEventListener('scroll', function () {
      sessionStorage.setItem(KEY_SCROLL, String(window.scrollY));
    });

    
    document.getElementById('printButton')?.addEventListener('click', function () {
      window.print();
    });
    document.getElementById('excelButton')?.addEventListener('click', function () {
      window.open(pdfUrlExcel, '_blank');
    });
  });
})();
