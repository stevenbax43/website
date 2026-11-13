(() => {
  function calculatePower(voltage, current, powerFactor) {
    const apparent = Math.sqrt(3) * voltage * current / 1000;
    const active = apparent * powerFactor;
    const reactive = apparent * Math.sqrt(Math.max(0, 1 - powerFactor ** 2));
    return { active, apparent, reactive };
  }

  function setVector(line, x1, y1, x2, y2) {
    line.setAttribute('x1', x1);
    line.setAttribute('y1', y1);
    line.setAttribute('x2', x2);
    line.setAttribute('y2', y2);
  }

  function setLabel(label, x, y, value) {
    label.setAttribute('x', x);
    label.setAttribute('y', y);
    label.textContent = value;
  }

  function drawPowerTriangle(power, powerFactor) {
    const originX = 140;
    const originY = 345;
    const horizontalLimit = 455;
    const verticalLimit = 250;
    const scale = power.apparent > 0
      ? Math.min(
        horizontalLimit / power.apparent,
        power.reactive > 0 ? verticalLimit / power.reactive : Infinity,
      )
      : 0;
    const activeLength = power.active * scale;
    const reactiveLength = power.reactive * scale;
    const endX = originX + activeLength;
    const endY = originY - reactiveLength;

    setVector(document.getElementById('vectorP'), originX, originY, endX, originY);
    setVector(document.getElementById('vectorQ'), endX, originY, endX, endY);
    setVector(document.getElementById('vectorS'), originX, originY, endX, endY);

    setLabel(
      document.getElementById('labelP'),
      originX + activeLength / 2,
      originY + 28,
      `P ${power.active.toFixed(2)} kW`,
    );
    setLabel(
      document.getElementById('labelQ'),
      endX + 14,
      originY - reactiveLength / 2,
      `Q ${power.reactive.toFixed(2)} kVAr`,
    );
    setLabel(
      document.getElementById('labelS'),
      originX + activeLength / 2 - 12,
      originY - reactiveLength / 2 - 14,
      `S ${power.apparent.toFixed(2)} kVA`,
    );

    const angle = Math.acos(Math.min(1, Math.max(0, powerFactor)));
    const radius = 42;
    const arcEndX = originX + radius * Math.cos(angle);
    const arcEndY = originY - radius * Math.sin(angle);
    document.getElementById('powerAngle').setAttribute(
      'd',
      `M ${originX + radius} ${originY} A ${radius} ${radius} 0 0 0 ${arcEndX} ${arcEndY}`,
    );
    setLabel(
      document.getElementById('labelPhi'),
      originX + (radius + 18) * Math.cos(angle / 2),
      originY - (radius + 18) * Math.sin(angle / 2),
      `φ ${((angle * 180) / Math.PI).toFixed(1)}°`,
    );

    document.getElementById('powerDiagramDescription').textContent =
      `Vermogensdriehoek: actief vermogen ${power.active.toFixed(2)} kilowatt, ` +
      `blindvermogen ${power.reactive.toFixed(2)} kilovoltampere reactief, ` +
      `schijnbaar vermogen ${power.apparent.toFixed(2)} kilovoltampere.`;
  }

  function updateValues() {
    const voltage = Number(document.getElementById('U_spanning').value);
    const current = Number(document.getElementById('I_stroom').value);
    const powerFactor = Number(document.getElementById('Phi_factor').value);
    const power = calculatePower(voltage, current, powerFactor);

    document.getElementById('P_actief').textContent = power.active.toFixed(2);
    document.getElementById('S_schijn').textContent = power.apparent.toFixed(2);
    document.getElementById('B_blind').textContent = power.reactive.toFixed(2);
    drawPowerTriangle(power, powerFactor);
  }

  function syncSliderAndInput(sliderId, inputId) {
    const slider = document.getElementById(sliderId);
    const input = document.getElementById(inputId);

    slider.addEventListener('input', () => {
      input.value = slider.value;
      updateValues();
    });

    input.addEventListener('input', () => {
      if (input.value === '') return;
      const value = Number(input.value);
      if (!Number.isFinite(value)) return;
      const boundedValue = Math.min(Number(slider.max), Math.max(Number(slider.min), value));
      slider.value = boundedValue;
      input.value = boundedValue;
      updateValues();
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    syncSliderAndInput('U_spanning', 'slider-value1');
    syncSliderAndInput('I_stroom', 'slider-value2');
    syncSliderAndInput('Phi_factor', 'slider-value3');

    document.getElementById('printButton')?.addEventListener('click', event => {
      event.preventDefault();
      window.print();
    });
    document.getElementById('excelButton')?.addEventListener('click', event => {
      event.preventDefault();
      window.open(pdfUrlExcel, '_blank', 'noopener');
    });

    updateValues();
  });
})();
