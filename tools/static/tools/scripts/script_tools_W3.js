// ==============================
// GLOBAL VARIABLES
// ==============================
let chart;

// System type
let systemType = "water";

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
const designLimits = {
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
    150:{ di: 160.3, t: 4.0, du: 168.3 },
    200:{ di: 207.9, t: 5.6, du: 219.1 }
};

// Standard round duct diameters (mm)
const ductSizes = [
    80, 100, 125, 160, 180, 200,
    224, 250, 280, 315, 355, 400,
    450, 500, 560, 630, 710, 800
];

// ==============================
// GENERIC FUNCTIONS
// ==============================

// Friction factor (Swamee-Jain)
function frictionFactor(roughness, d, reynolds) {
    const term1 = roughness / (3.72 * d);
    const term2 = 5.74 / Math.pow(reynolds, 0.9);
    const inv = -2 * Math.log10(term1 + term2);
    return 1 / (inv * inv);
}

// Get active fluid properties
function getFluidProps() {
    return systemType === "water" ? waterProps : airProps;
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
function updateFlowControls() {

    const input = document.getElementById("flowInput");
    const slider = document.getElementById("flowSlider");
    const unitSelect = document.getElementById("unitSelect");

    if (systemType === "air") {

        // Slider instellingen lucht
        slider.min = 0;
        slider.max = 5000;
        slider.step = 10;

        input.min = 0;
        input.max = 10000;
        input.step = 10;

        input.value = 200;
        slider.value = 200;

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
// TABLE UPDATE
// ==============================

function updateTable() {

    const flowInput = parseFloat(document.getElementById("flowInput").value);
    const unit = document.getElementById("unitSelect").value;

    const results = systemType === "water"
        ? calculatePipes(flowInput, unit)
        : calculateDucts(flowInput, unit);

    const selected = selectBest(results);

    const table = document.getElementById("resultTable");
    table.innerHTML = "";

    if (!selected) {
        table.innerHTML = `<tr><td colspan="6">Geen geschikte maat gevonden</td></tr>`;
        return;
    }

    const rows = getNeighbors(results, selected);

    rows.forEach(r => {

        const tr = document.createElement("tr");

        if (r.dn === selected.dn) {
            tr.classList.add("selected-dn");
        } else {
            tr.classList.add("neighbor-dn");
        }

        tr.innerHTML = `
            <td>${r.dn}</td>
            <td>${r.di.toFixed(1)}</td>
            <td>${r.t}</td>
            <td>${r.du.toFixed(1)}</td>
            <td>${r.velocity.toFixed(2)}</td>
            <td>${Math.round(r.dp)}</td>
        `;

        table.appendChild(tr);
    });

    updateChart(results, selected);
}

// ==============================
// CHART
// ==============================

function updateChart(results, selected) {

    const labels = results.map(r => r.dn);
    const velocities = results.map(r => r.velocity);
    const dpValues = results.map(r => r.dp);

    const isAir = systemType === "air";

    // 👉 Dynamische schaal
    const maxVelocity = Math.max(...velocities) * 1.3;
    const maxDp = Math.max(...dpValues) * 1.3;

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
                    type: 'logarithmic',
                    position: 'left',
                    min: isAir ? 0 : undefined,
                    max: maxVelocity,
                    title: {
                        display: true,
                        text: 'Log Snelheid (m/s)'
                    }
                },

                // 👉 PRESSURE LOSS
                y1: {
                    type: 'logarithmic',
                    position: 'right',
                    min: isAir ? 0 : undefined,
                    max: maxDp,
                    title: {
                        display: true,
                        text: 'Log Drukverlies (Pa/m)'
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
// EVENTS
// ==============================

// Input sync
const input = document.getElementById("flowInput");
const slider = document.getElementById("flowSlider");

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
document.getElementById("velLimit").addEventListener("input", () => {
    designLimits.velocityMax = parseFloat(document.getElementById("velLimit").value);
    updateTable();
});

document.getElementById("dpLimit").addEventListener("input", () => {
    designLimits.dpMax = parseFloat(document.getElementById("dpLimit").value);
    updateTable();
});

// System type switch (ADD THIS IN HTML)
const systemSelect = document.getElementById("systemType");

if (systemSelect) {
    systemSelect.addEventListener("change", () => {

        systemType = systemSelect.value;

        if (systemType === "air") {
            designLimits.velocityMax = 6;
            designLimits.dpMax = 1;
        } else {
            designLimits.velocityMax = 1.5;
            designLimits.dpMax = 150;
        }

        document.getElementById("velLimit").value = designLimits.velocityMax;
        document.getElementById("dpLimit").value = designLimits.dpMax;

        updateFlowControls();   // 🔥 NIEUW
        updateTable();
    });
}

// INIT
document.addEventListener("DOMContentLoaded", () => {
    updateFlowControls();  // 🔥 belangrijk
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