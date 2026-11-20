// ==============================
// GLOBAL VARIABLES
// ==============================
let chart;

// System type
let systemType = "pipes";

// ==============================
// CONSTANTS
// ==============================

// Water
const waterProps = {
    density: 999.65,
    kinematicViscosity: 1.31e-6,
    roughness: 4.5e-5
};

// Air
const airProps = {
    density: 1.2,
    kinematicViscosity: 1.5e-5,
    roughness: 9e-5
};

// Default design limits
let ductShape = "round";

const designLimits = {
    velocityMin: 0.5,
    velocityMax: 1.5,
    dpMax: 150
};
// ==============================
// DATA
// ==============================

// Pipe data
const pipeData = {
    15: { di: 12.6, t: 1.2, du: 15.0 },
    20: { di: 19.0, t: 1.5, du: 22.0 },
    25: { di: 25.0, t: 1.5, du: 28.0 },
    32: { di: 32.0, t: 1.5, du: 35.0 },
    40: { di: 39.0, t: 1.5, du: 42.0 },
    50: { di: 51.0, t: 1.5, du: 54.0 },
    65: { di: 70.9, t: 2.6, du: 76.1 },
    80: { di: 83.1, t: 2.9, du: 88.9 },
    100:{ di: 107.1, t: 3.6, du: 114.3 },
    125:{ di: 131.7, t: 4.0, du: 139.7 },
    160:{ di: 160.3, t: 4.0, du: 168.3 },
    200:{ di: 207.9, t: 5.6, du: 219.1 }
};

// Standard round duct diameters (mm)
const ductSizes = [
    100, 125, 160, 200,
    250, 315, 355, 400,
    450, 500, 560, 630, 710, 800
];


// ==============================
// GENERIC FUNCTIONS
// ==============================

// Friction factor (Swamee-Jain)
function frictionFactor(roughness, d, reynolds) {

    if (
        !Number.isFinite(reynolds) ||
        reynolds <= 0 ||
        !Number.isFinite(d) ||
        d <= 0
    ) {
        return 0;
    }

    // Laminaire stroming
    if (reynolds < 2300) {
        return 64 / reynolds;
    }

    // Turbulente stroming: Swamee-Jain
    const term1 = roughness / (3.7 * d);
    const term2 = 5.74 / Math.pow(reynolds, 0.9);
    const inv = -2 * Math.log10(term1 + term2);

    return 1 / Math.pow(inv, 2);
}

// Get active fluid properties
function getFluidProps() {
    return systemType === "pipes" ? waterProps : airProps;
}

// Convert flow to m³/s
function convertFlow(flowInput, unit) {
    return unit === "ls"
        ? flowInput / 1000
        : flowInput / 3600;
}

// ==============================
// CALCULATIONS
// ==============================

// WATER PIPES
function calculatePipes(flowInput, unit) {

    const flow = convertFlow(flowInput, unit);
    const { density, kinematicViscosity, roughness } = getFluidProps();

    const results = [];

    for (const dn in pipeData) {

        const di_mm = pipeData[dn].di;
        const d = di_mm / 1000;

        const area = Math.PI * d * d / 4;
        const velocity = flow / area;
        const reynolds = velocity * d / kinematicViscosity;

        const lambda = frictionFactor(roughness, d, reynolds);

        const dp = lambda * (1 / d) * 0.5 * density * velocity * velocity;

        results.push({
            dn: parseInt(dn),
            di: di_mm,
            t: pipeData[dn].t,
            du: pipeData[dn].du,
            velocity,
            dp
        });
    }

    return results.sort((a, b) => a.dn - b.dn);
}

// AIR DUCTS
function calculateDucts(flowInput, unit) {

    const flow = convertFlow(flowInput, unit);
    const { density, kinematicViscosity, roughness } = getFluidProps();

    const results = [];

    ductSizes.forEach(d_mm => {

        const d = d_mm / 1000;

        const area = Math.PI * d * d / 4;
        const velocity = flow / area;
        const reynolds = velocity * d / kinematicViscosity;

        const lambda = frictionFactor(roughness, d, reynolds);

        const dp = lambda * (1 / d) * 0.5 * density * velocity * velocity;

        results.push({
            dn: d_mm,
            di: d_mm,
            t: "-",
            du: d_mm,
            velocity,
            dp
        });
    });

    return results.sort((a, b) => a.dn - b.dn);
}

// ==============================
// SELECTION LOGIC
// ==============================

function selectBest(results) {
    return results.find(r =>
        r.velocity <= designLimits.velocityMax &&
        r.dp <= designLimits.dpMax
    );
}

function getNeighbors(results, selected) {
    const index = results.findIndex(r => r.dn === selected.dn);

    return [
        results[index - 1],
        results[index],
        results[index + 1]
    ].filter(Boolean);
}
function updateSystemIcon() {

    const systemIcon =
        document.getElementById("systemIcon");

    if (!systemIcon) {
        return;
    }

    if (systemType === "ducts") {
        systemIcon.innerHTML =
            '<i class="fas fa-wind"></i>';
    } else {
        systemIcon.innerHTML =
            '<i class="fas fa-tint"></i>';
    }
}
function updateFlowControls() {

    const input = document.getElementById("flowInput");
    const slider = document.getElementById("flowSlider");
    const unitSelect = document.getElementById("unitSelect");
    const defaultAirFlow =
        ductShape === "rectangular" ? 2000 : 200;


    if (systemType === "ducts") {

        // Slider instellingen lucht
        slider.min = 0;
        slider.max = 20000;
        slider.step = 10;

        input.min = 0;
        input.max = 20000;
        input.step = 10;
        
        input.value = defaultAirFlow;
        slider.value = defaultAirFlow;

        // 👉 UNIT LOCKEN
        unitSelect.value = "m3h";
        unitSelect.disabled = true;

    } else {

        // Slider instellingen water
        slider.min = 0;
        slider.max = 55;
        slider.step = 0.1;

        input.min = 0;
        input.max = 55;
        input.step = 0.1;

        input.value = 1;
        slider.value = 1;

        // 👉 UNIT TERUG VRIJGEVEN
        unitSelect.disabled = false;
    }
}

// ==============================
// CHART
// ==============================

function updateChart(results, selected) {

    const labels = results.map(r => r.dn);
    const velocities = results.map(r => r.velocity);
    const dpValues = results.map(r => r.dp);

    const isAir = systemType === "ducts";

    // 👉 Dynamische schaal
    const maxVelocity = Math.max(
        designLimits.velocityMax * 1.3,
        ...velocities.map(value => value * 1.3),
        1
    );

    const maxDp = Math.max(
        designLimits.dpMax * 1.3,
        ...dpValues.map(value => value * 1.3),
        0.1
    );

    if (chart) chart.destroy();

    const ctx = document.getElementById('dnChart').getContext('2d');

    chart = new Chart(ctx, {
        type: 'bar',

        data: {
            labels: labels,

            datasets: [
                {
                    type: 'bar',
                    label: 'Snelheid [m/s]',
                    data: velocities,

                    backgroundColor: results.map(r => {
                        if (r.dn === selected.dn) return "rgba(25,135,84,0.9)";
                        if (r.velocity > designLimits.velocityMax || r.dp > designLimits.dpMax)
                            return "rgba(220,53,69,0.7)";
                        return isAir
                            ? "rgba(255,193,7,0.6)"   // air = geel
                            : "rgba(13,110,253,0.5)"; // water = blauw
                    })
                },
                {
                    type: 'line',
                    label: 'Drukverlies [Pa/m]',
                    data: dpValues,
                    borderColor: 'black',
                    backgroundColor: 'black',
                    borderDash: [6, 6],
                    tension: 0.3,
                    pointRadius: 3,
                    yAxisID: 'y1'
                }
            ]
        },

        options: {
            responsive: true,

            plugins: {
                legend: {
                    display: true
                },

                annotation: {
                    annotations: {

                        velocityLimit: {
                            type: 'line',
                            yMin: designLimits.velocityMax,
                            yMax: designLimits.velocityMax,
                            yScaleID: 'y',
                            borderColor: 'red',
                            borderWidth: 2,
                            label: {
                                display: true,
                                content: `Max ${designLimits.velocityMax} m/s`
                            }
                        },

                        pressureLimit: {
                            type: 'line',
                            yMin: designLimits.dpMax,
                            yMax: designLimits.dpMax,
                            yScaleID: 'y1',
                            borderColor: 'red',
                            borderWidth: 2,
                            borderDash: [6, 6],
                            label: {
                                display: true,
                                content: `Max ${designLimits.dpMax} Pa/m`
                            }
                        }
                    }
                }
            },

            scales: {

                // 👉 VELOCITY
                y: {
                    type: "logarithmic",
                    position: "left",
                    min: 0.1,
                    max: maxVelocity,
                    title: {
                        display: true,
                        text: "Log Snelheid (m/s)"
                    }
                },

                // 👉 PRESSURE LOSS
                y1: {
                    type: "logarithmic",
                    position: "right",
                    min: 0.01,
                    max: maxDp,
                    title: {
                        display: true,
                        text: "Log Drukverlies (Pa/m)"
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                },

                x: {
                    title: {
                        display: true,
                        text: isAir ? 'Diameter (mm)' : 'DN'
                    }
                }
            }
        }
    });
}

// ==============================
// RECTANGULAR AIR DUCTS
// ==============================

function calculateRectangularDuct(flowInput, unit, widthMm, heightMm) {

    const flow = convertFlow(flowInput, unit);
    const { density, kinematicViscosity, roughness } = airProps;

    const width = widthMm / 1000;
    const height = heightMm / 1000;

    const area = width * height;

    if (area <= 0 || flow <= 0) {
        return {
            widthMm,
            heightMm,
            area: 0,
            velocity: 0,
            hydraulicDiameter: 0,
            reynolds: 0,
            lambda: 0,
            dp: 0,
            aspectRatio: 0
        };
    }

    const velocity = flow / area;

    // Hydraulische diameter rechthoekig kanaal
    const hydraulicDiameter =
        (2 * width * height) / (width + height);

    const reynolds =
        velocity * hydraulicDiameter / kinematicViscosity;

    const lambda = frictionFactor(
        roughness,
        hydraulicDiameter,
        reynolds
    );

    const dp =
        lambda *
        (1 / hydraulicDiameter) *
        0.5 *
        density *
        velocity *
        velocity;

    const aspectRatio =
        Math.max(widthMm, heightMm) /
        Math.min(widthMm, heightMm);

    return {
        widthMm,
        heightMm,
        area,
        velocity,
        hydraulicDiameter,
        reynolds,
        lambda,
        dp,
        aspectRatio
    };
}

function getRectangularCellClass(result) {

    const maxAspectRatio = parseFloat(
        document.getElementById("maxAspectRatio").value
    );

    if (
        result.velocity > designLimits.velocityMax ||
        result.dp > designLimits.dpMax
    ) {
        return "duct-speed-high";
    }

    if (result.velocity < designLimits.velocityMin) {
        return "duct-speed-low";
    }

    if (result.aspectRatio > maxAspectRatio) {
        return "duct-speed-ratio";
    }

    return "duct-speed-good";
}

function updateRectangularMatrix() {

    const matrixBlock =
        document.getElementById("rectangularMatrixBlock");

    if (
        systemType !== "ducts" ||
        ductShape !== "rectangular"
    ) {
        matrixBlock.classList.add("d-none");
        return;
    }

    matrixBlock.classList.remove("d-none");

    const flowInput = parseFloat(
        document.getElementById("flowInput").value
    );

    const unit =
        document.getElementById("unitSelect").value;

    const minSize = parseInt(
        document.getElementById("matrixMinSize").value
    );

    const maxSize = parseInt(
        document.getElementById("matrixMaxSize").value
    );

    const step = parseInt(
        document.getElementById("matrixStep").value
    );

    const table =
        document.getElementById("ductMatrix");

    const thead = table.querySelector("thead");
    const tbody = table.querySelector("tbody");

    thead.innerHTML = "";
    tbody.innerHTML = "";

    const selection =
    document.getElementById("rectangularSelection");

    selection.innerHTML =
        "Klik op een kanaalmaat om de eigenschappen te bekijken.";


    if (
        !Number.isFinite(flowInput) ||
        flowInput <= 0 ||
        !Number.isFinite(minSize) ||
        !Number.isFinite(maxSize) ||
        !Number.isFinite(step) ||
        minSize <= 0 ||
        maxSize < minSize ||
        step <= 0
    ) {
        tbody.innerHTML = `
            <tr>
                <td class="text-danger p-3">
                    Controleer debiet en matrixinstellingen.
                </td>
            </tr>
        `;
        return;
    }

    const sizes = [];

    for (
        let size = minSize;
        size <= maxSize;
        size += step
    ) {
        sizes.push(size);
    }

    // Header: hoogte op x-as
    const headerRow = document.createElement("tr");

    const cornerHeader = document.createElement("th");
    cornerHeader.innerHTML = `
        Breedte ↓<br>
        Hoogte →
    `;

    headerRow.appendChild(cornerHeader);

    sizes.forEach(height => {
        const th = document.createElement("th");
        th.textContent = `${height} mm`;
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);

    // Rijen: breedte op y-as
    sizes.forEach(width => {

        const row = document.createElement("tr");

        const rowHeader = document.createElement("th");
        rowHeader.textContent = `${width} mm`;

        row.appendChild(rowHeader);

        sizes.forEach(height => {

            const result = calculateRectangularDuct(
                flowInput,
                unit,
                width,
                height
            );

            const td = document.createElement("td");

            td.classList.add(
                "duct-cell",
                getRectangularCellClass(result)
            );

            td.innerHTML = `
                ${result.velocity.toFixed(1)}
                <span class="duct-cell-dimension">
                    ${width} × ${height}
                </span>
            `;

            td.title =
                `${width} × ${height} mm | ` +
                `${result.velocity.toFixed(2)} m/s | ` +
                `${result.dp.toFixed(2)} Pa/m`;

            td.addEventListener("click", () => {

                table
                    .querySelectorAll(".duct-cell.selected")
                    .forEach(cell =>
                        cell.classList.remove("selected")
                    );

                td.classList.add("selected");

                showRectangularSelection(result);
            });

            row.appendChild(td);
        });

        tbody.appendChild(row);
    });
}

function showRectangularSelection(result) {

    const selection =
        document.getElementById("rectangularSelection");

    const hydraulicDiameterMm =
        result.hydraulicDiameter * 1000;

    selection.innerHTML = `
        <div class="duct-selection-grid">

            <div class="duct-selection-item">
                <small>Kanaalmaat</small>
                <strong>
                    ${result.widthMm} × ${result.heightMm} mm
                </strong>
            </div>

            <div class="duct-selection-item">
                <small>Snelheid</small>
                <strong>
                    ${result.velocity.toFixed(2)} m/s
                </strong>
            </div>

            <div class="duct-selection-item">
                <small>Drukverlies</small>
                <strong>
                    ${result.dp.toFixed(2)} Pa/m
                </strong>
            </div>

            <div class="duct-selection-item">
                <small>Hydraulische diameter</small>
                <strong>
                    ${hydraulicDiameterMm.toFixed(0)} mm
                </strong>
            </div>

            <div class="duct-selection-item">
                <small>Kanaalverhouding</small>
                <strong>
                    1 : ${result.aspectRatio.toFixed(1)}
                </strong>
            </div>

        </div>
    `;
}

// ==============================
// TABLE UPDATE
// ==============================

function updateTable() {

    const flowInput = parseFloat(
        document.getElementById("flowInput").value
    );

    const unit =
        document.getElementById("unitSelect").value;

    const roundResultBlock =
        document.getElementById("roundResultBlock");

    const chartBlock =
        document.getElementById("chartBlock");

    const rectangularMatrixBlock =
        document.getElementById("rectangularMatrixBlock");

    if (
        !roundResultBlock ||
        !chartBlock ||
        !rectangularMatrixBlock
    ) {
        console.error(
            "Een of meerdere resultaatblokken ontbreken in de HTML."
        );
        return;
    }

    if (
        systemType === "ducts" &&
        ductShape === "rectangular"
    ) {
        roundResultBlock.classList.add("d-none");
        chartBlock.classList.add("d-none");
        rectangularMatrixBlock.classList.remove("d-none");

        if (chart) {
            chart.destroy();
            chart = null;
        }

        updateRectangularMatrix();
        return;
    }

    roundResultBlock.classList.remove("d-none");
    chartBlock.classList.remove("d-none");
    rectangularMatrixBlock.classList.add("d-none");

    const results = systemType === "pipes"
        ? calculatePipes(flowInput, unit)
        : calculateDucts(flowInput, unit);

    const selected = selectBest(results);

    const table =
        document.getElementById("resultTable");

    table.innerHTML = "";

    if (!selected) {
        table.innerHTML = `
            <tr>
                <td colspan="6">
                    Geen geschikte maat gevonden
                </td>
            </tr>
        `;

        if (chart) {
            chart.destroy();
            chart = null;
        }

        return;
    }

    const rows = getNeighbors(results, selected);

    rows.forEach(result => {

        const tr = document.createElement("tr");

        tr.classList.add(
            result.dn === selected.dn
                ? "selected-dn"
                : "neighbor-dn"
        );

        tr.innerHTML = `
            <td>${result.dn}</td>
            <td>${result.di.toFixed(1)}</td>
            <td>${result.t}</td>
            <td>${result.du.toFixed(1)}</td>
            <td>${result.velocity.toFixed(2)}</td>
            <td>${result.dp.toFixed(2)}</td>
        `;

        table.appendChild(tr);
    });

    updateChart(results, selected);
}
// ==============================
// EVENTS
// ==============================

// Input sync
const input = document.getElementById("flowInput");
const slider = document.getElementById("flowSlider");
[
    "matrixMinSize",
    "matrixMaxSize",
    "matrixStep",
    "maxAspectRatio"
].forEach(id => {

    const element = document.getElementById(id);

    if (element) {
        element.addEventListener("input", updateRectangularMatrix);
        element.addEventListener("change", updateRectangularMatrix);
    }
});

slider.addEventListener("input", () => {
    input.value = slider.value;
    updateTable();
});

input.addEventListener("input", () => {
    slider.value = input.value;
    updateTable();
});


// Unit change
document.getElementById("unitSelect").addEventListener("change", updateTable);

// Design limits
document.getElementById("velMax").addEventListener("input", () => {
    designLimits.velocityMax = parseFloat(document.getElementById("velMax").value);
    updateTable();
});

document.getElementById("dpLimit").addEventListener("input", () => {
    designLimits.dpMax = parseFloat(document.getElementById("dpLimit").value);
    updateTable();
});

document
    .getElementById("velMin").addEventListener("input", () => {
        designLimits.velocityMin = parseFloat(document.getElementById("velMin").value);
        updateTable();
    });

// ==============================
// SYSTEM AND DUCT SHAPE EVENTS
// ==============================

const systemSelect =
    document.getElementById("systemType");

const ductShapeSelect =
    document.getElementById("ductShape");

const ductShapeBlock =
    document.getElementById("ductShapeBlock");

// Kanaalvorm wijzigen
if (ductShapeSelect) {
    ductShapeSelect.addEventListener("change", () => {

        ductShape = ductShapeSelect.value;

        if (ductShape === "rectangular") {
            input.value = 2000;
            slider.value = 2000;

            const unitSelect =
                document.getElementById("unitSelect");

            unitSelect.value = "m3h";
        }

        updateTable();
    });
}

// Systeem wijzigen
if (systemSelect) {
    systemSelect.addEventListener("change", () => {

        systemType = systemSelect.value;
        updateSystemIcon();
        if (systemType === "ducts") {

            if (ductShapeBlock) {
                ductShapeBlock.classList.remove("d-none");
            }

            ductShape = ductShapeSelect
                ? ductShapeSelect.value
                : "round";

            designLimits.velocityMin = 3;
            designLimits.velocityMax = 6;
            designLimits.dpMax = 1;

        } else {

            if (ductShapeBlock) {
                ductShapeBlock.classList.add("d-none");
            }

            ductShape = "round";

            if (ductShapeSelect) {
                ductShapeSelect.value = "round";
            }

            designLimits.velocityMin = 0.5;
            designLimits.velocityMax = 1.5;
            designLimits.dpMax = 150;
        }

        document.getElementById("velMin").value =
            designLimits.velocityMin;

        document.getElementById("velMax").value =
            designLimits.velocityMax;

        document.getElementById("dpLimit").value =
            designLimits.dpMax;

        updateFlowControls();
        updateTable();
    });
}
// ==============================
// INIT
// ==============================
document.addEventListener("DOMContentLoaded", () => {

    // Beginwaarden uitlezen uit de dropdowns
    if (systemSelect) {
        systemType = systemSelect.value;
    }

    if (ductShapeSelect) {
        ductShape = ductShapeSelect.value;
    }

    // Kanaalvorm alleen tonen bij luchtkanalen
    if (ductShapeBlock) {
        ductShapeBlock.classList.toggle(
            "d-none",
            systemType !== "ducts"
        );
    }

    // Ontwerpcriteria instellen
    if (systemType === "ducts") {
        designLimits.velocityMin = 3;
        designLimits.velocityMax = 6;
        designLimits.dpMax = 1;
    } else {
        designLimits.velocityMin = 0.5;
        designLimits.velocityMax = 1.5;
        designLimits.dpMax = 150;
    }

    document.getElementById("velMin").value =
        designLimits.velocityMin;

    document.getElementById("velMax").value =
        designLimits.velocityMax;

    document.getElementById("dpLimit").value =
        designLimits.dpMax;
        
    updateSystemIcon();
    updateFlowControls();
    updateTable();
});
document.addEventListener("DOMContentLoaded", function () {

    const collapseElement = document.getElementById('formulaBlock');

    if (collapseElement) {
        new bootstrap.Collapse(collapseElement, {
            toggle: false
        });
    }

});