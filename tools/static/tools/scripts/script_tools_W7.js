(() => {
  const tool = document.getElementById("w7Tool");
  if (!tool) return;

  const sourceLevels = document.getElementById("sourceLevels");
  const csrfToken = tool.querySelector("[name=csrfmiddlewaretoken]").value;

  function numberValue(id) {
    const input = document.getElementById(id);
    if (!input || input.value.trim() === "") throw new Error("Vul alle verplichte velden in.");
    const value = Number(input.value);
    if (!Number.isFinite(value)) throw new Error("Vul geldige getallen in.");
    return value;
  }

  function format(value) {
    return Number(value).toLocaleString("nl-NL", {
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
    });
  }

  function payloadFor(calculation) {
    if (calculation === "sum") {
      return {
        calculation,
        levels: [...sourceLevels.querySelectorAll(".source-level input")].map((input) => {
          if (input.value.trim() === "") throw new Error("Vul alle geluidsniveaus in.");
          return Number(input.value);
        }),
      };
    }
    if (calculation === "spectrum") {
      return {
        calculation,
        levels: [...document.querySelectorAll(".spectrum-level")].map((input) => (
          input.value.trim() === "" ? null : Number(input.value)
        )),
      };
    }
    if (calculation === "distance") {
      return {
        calculation,
        lw_db: numberValue("lwDb"),
        directivity_factor: numberValue("directivity"),
        distance_m: numberValue("distance"),
      };
    }
    return {
      calculation: "equivalent",
      lp_a_db: numberValue("lpA"),
      operating_hours: numberValue("operatingHours"),
      assessment_hours: numberValue("assessmentHours"),
    };
  }

  async function calculate(button) {
    const kind = button.dataset.calculation;
    const prefix = kind === "sum" ? "sum" : kind;
    const error = document.getElementById(`${prefix}Error`);
    error.textContent = "";
    button.disabled = true;
    try {
      const response = await fetch(tool.dataset.calculateUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify(payloadFor(kind)),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "De berekening is niet gelukt.");

      if (kind === "sum") {
        document.getElementById("sumResult").textContent = `Resultaat: ${format(data.total_db)} dB`;
      } else if (kind === "spectrum") {
        document.getElementById("spectrumUnweightedResult").textContent = `Totaal Lw: ${format(data.total_db)} dB`;
        document.getElementById("spectrumResult").textContent = `Totaal Lp,A: ${format(data.total_db_a)} dB(A)`;
        document.getElementById("spectrumDetails").innerHTML = data.bands.map((band) => (
          `<div class="spectrum-detail"><span>${band.frequency_hz} Hz: ${format(band.level_db)} ${band.correction_db >= 0 ? "+" : ""}${band.correction_db} dB</span><strong>${format(band.level_a_db)} dB(A)</strong></div>`
        )).join("");
      } else if (kind === "distance") {
        document.getElementById("distanceResult").textContent = `Lp: ${format(data.lp_db)} dB`;
      } else {
        document.getElementById("equivalentResult").textContent = `LA,eq: ${format(data.laeq_db)} dB(A)`;
      }
    } catch (errorValue) {
      error.textContent = errorValue.message || "De berekening is niet gelukt.";
    } finally {
      button.disabled = false;
    }
  }

  function updateSources() {
    const rows = [...sourceLevels.querySelectorAll(".source-level")];
    rows.forEach((row, index) => {
      row.querySelector(".input-group-text").textContent = `Bron ${index + 1}`;
      const input = row.querySelector("input");
      input.setAttribute("aria-label", `Geluidsniveau bron ${index + 1}`);
      row.querySelector(".remove-source").disabled = rows.length <= 1;
    });
  }

  document.getElementById("addSource").addEventListener("click", () => {
    if (sourceLevels.children.length >= 50) return;
    const row = document.createElement("div");
    row.className = "input-group source-level";
    row.innerHTML = `<span class="input-group-text"></span><input class="form-control" type="number" step="any" aria-label="Geluidsniveau" required><span class="input-group-text">dB</span><button class="btn btn-outline-secondary remove-source" type="button" aria-label="Verwijder geluidsbron">&times;</button>`;
    sourceLevels.appendChild(row);
    updateSources();
    row.querySelector("input").focus();
  });

  sourceLevels.addEventListener("click", (event) => {
    const button = event.target.closest(".remove-source");
    if (!button || sourceLevels.children.length <= 1) return;
    button.closest(".source-level").remove();
    updateSources();
  });

  document.querySelectorAll(".calculate-button").forEach((button) => {
    button.addEventListener("click", () => calculate(button));
  });
  document.getElementById("printButton").addEventListener("click", () => window.print());
})();
