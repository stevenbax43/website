/* ============================================================
   TOOL A5 – SCRIPT
   Strikte scheiding:
   - Search UI (boven)
   - NL-SfB boom (onder, passief)
   ============================================================ */

document.addEventListener("DOMContentLoaded", () => {
    initSearch();
    initNlsfbTree();
});

/* ============================================================
   DEEL 1 – ZOEKFUNCTIONALITEIT (STRICT GESCOPED)
   ============================================================ */

function initSearch() {
    const searchZone = document.getElementById("search-zone");
    if (!searchZone) return;

    const searchInput = searchZone.querySelector("#search");
    const resultsSection = searchZone.querySelector("#results-advice");
    const cardsContainer = searchZone.querySelector("#results-cards");
    const contextExplanation = searchZone.querySelector("#context-explanation");

    let abortController = null;

    searchInput.addEventListener("input", async () => {
        const query = searchInput.value.trim();

        if (query.length < 2) {
            hideResults();
            return;
        }

        if (abortController) abortController.abort();
        abortController = new AbortController();

        try {
            const response = await fetch(
                `/tools/api/sfb-search/?q=${encodeURIComponent(query)}`,
                { signal: abortController.signal }
            );

            const data = await response.json();
            if (!data.routes || Object.keys(data.routes).length === 0) {
                hideResults();
                return;
            }

            renderResults(data, query);

        } catch (err) {
            if (err.name !== "AbortError") {
             //   console.error("Zoekfout:", err);
            }
        }
    });

    function hideResults() {
        resultsSection.classList.add("d-none");
        cardsContainer.innerHTML = "";
        contextExplanation.classList.add("d-none");
    }

    function renderResults(data, query) {
        resultsSection.classList.remove("d-none");
        cardsContainer.innerHTML = "";
        contextExplanation.classList.add("d-none");

        const contextCode = detectContextFromQuery(query);
        let hasUncertain = false;

        for (const [route, items] of Object.entries(data.routes)) {
            if (!items?.length) continue;

            const uncertain = items.filter(i => i.uncertain === true);

            if (uncertain.length > 1 && contextCode) {
                const resolved = uncertain.find(i => i.code === contextCode);
                if (resolved) {
                    cardsContainer.appendChild(createScopeCard(route, resolved));
                    continue;
                }
            }

            if (uncertain.length > 1) {
                hasUncertain = true;
                cardsContainer.appendChild(createUncertainScopeCard(route, uncertain));
                continue;
            }

            cardsContainer.appendChild(createScopeCard(route, items[0]));
        }

        if (hasUncertain) {
            contextExplanation.classList.remove("d-none");
        }
    }
}

function detectContextFromQuery(query) {
    const q = query.toLowerCase();
    if (q.includes("koel")) return "55";
    if (q.includes("verwarm") || q.includes("cv")) return "56";
    return null;
}
function createScopeCard(route, item) {
    const titleMap = {
        werktuigbouwkundig: "Werktuigbouwkundig",
        brandveiligheid: "Brandveiligheid",
        besturing: "Besturing",
        elektrotechnisch: "Elektrotechnisch",
        bouwkundig: "Bouwkundig",
    };

    const scopeClassMap = {
        installateur: "bg-success",
        functioneel: "bg-warning text-dark",
        afstemming: "bg-secondary",
    };

    const col = document.createElement("div");
    col.className = "col-md-6";

    col.innerHTML = `
        <div class="card h-100 search-card" data-nlsfb-code="${item.code}">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <h6 class="mb-1">${titleMap[route] || route}</h6>
                    <span class="badge ${scopeClassMap[item.scope] || "bg-light text-dark"}">
                        ${item.scope || "onbekend"}
                    </span>
                </div>
                <div class="mt-2">
                    <strong>NL‑SfB ${item.code}</strong><br>
                    <span class="text-muted">${item.omschrijving}</span>
                </div>
            </div>
        </div>
    `;

    col.querySelector(".search-card").addEventListener("click", () => {
        openAndHighlightNlSfb(item.code);
    });

    return col;
}


function createUncertainScopeCard(route, items) {
    const col = document.createElement("div");
    col.className = "col-md-6";

    col.innerHTML = `
        <div class="card h-100 border-warning">
            <div class="card-body">
                <h6>${route}</h6>
                <span class="badge bg-warning text-dark mb-2 d-inline-block">
                    Context nodig
                </span>

                <p class="mt-2">
                    Dit element kan onder meerdere NL‑SfB categorieën vallen:
                </p>

                ${items.map((item, idx) => `
                    <div class="form-check">
                        <input class="form-check-input"
                               type="radio"
                               name="${route}-choice"
                               id="${route}-${idx}"
                               value="${item.code}">
                        <label class="form-check-label" for="${route}-${idx}">
                            <strong>${item.code}</strong> – ${item.omschrijving}
                        </label>
                    </div>
                `).join("")}

            </div>
        </div>
    `;

    return col;
}
/* ============================================================
   DEEL 2 – NL-SfB BOOM (PASSIEF, BACKEND-GEDREVEN)
   ============================================================ */

function initNlsfbTree() {
    const treeZone = document.getElementById("nlsfb-tree");
    if (!treeZone) return;

    enableNlSfbClicks(treeZone);
}

function getNlSfbPath(code) {
    // Voorbeeld: "59.3" → ["5-", "59", "59.3"]
    const parts = [];
    if (!code) return parts;

    // hoofdstuk
    parts.push(code.charAt(0) + "-");

    if (!code.includes(".")) {
        parts.push(code);
        return parts;
    }

    const segments = code.split(".");
    for (let i = 0; i < segments.length; i++) {
        parts.push(segments.slice(0, i + 1).join("."));
    }

    return [...new Set(parts)];
}

function enableNlSfbClicks(scope) {
    scope.querySelectorAll("tr[data-nlsfb]").forEach(row => {
        
        if (row.dataset.bound) return;
        row.dataset.bound = "true";


        
        row.addEventListener("click", async event => {
            event.stopPropagation();
            await toggleNlSfbRow(row, row.dataset.nlsfb);
        });

    });
}

const nlSfbCache = {};

async function fetchChildren(code) {

    if (nlSfbCache[code]) {
        return nlSfbCache[code];
    }

    const response = await fetch(
        `/tools/nl-sfb/nlsfb/children/${encodeURIComponent(code)}/`
    );

    const children = response.ok
        ? await response.json()
        : [];

    nlSfbCache[code] = children;

    return children;
}

async function toggleNlSfbRow(row, code) {
    if (row.nextElementSibling?.classList.contains("nlsfb-children")) {
        row.nextElementSibling.remove();
        row.classList.remove("table-active");
        return;
    }

    
try {

        const children = await fetchChildren(code);

        if (!children.length) return;

        row.classList.add("table-active");

        const tr = document.createElement("tr");
        tr.classList.add("nlsfb-children");

        const td = document.createElement("td");
        td.colSpan = 2;

        td.innerHTML = `
            <div class="ps-4">
                <table class="table table-sm table-hover mb-0">
                    <tbody>
                        ${children.map(c => `
                            <tr data-nlsfb="${c.code}">
                                <td style="width:140px">
                                    <strong>${c.code}</strong>
                                </td>
                                <td>${c.omschrijving}</td>
                            </tr>
                        `).join("")}
                    </tbody>
                </table>
            </div>
        `;

        tr.appendChild(td);
        row.after(tr);

        enableNlSfbClicks(tr);

    } catch (e) {
        //console.error("NL‑SfB boom fout:", e);
    }
}
async function openAndHighlightNlSfb(code) {
    const path = getNlSfbPath(code);

    // oude highlights opruimen
    document.querySelectorAll(".nlsfb-highlight")
        .forEach(el => el.classList.remove("nlsfb-highlight"));

    let previousRow = null;

    for (const step of path) {
        
        
        const rows = document.querySelectorAll(
            `tr[data-nlsfb="${step}"]`
        );

        if (!rows.length) {
            continue;
        }

        const row = rows[rows.length - 1];

        // als deze nog niet open is, open hem
        if (!row.nextElementSibling?.classList.contains("nlsfb-children")) {
            await toggleNlSfbRow(row, step);
        }

        previousRow = row;
    }

    // highlight laatste stap
    if (previousRow) {
        previousRow.classList.add("nlsfb-highlight");
        previousRow.scrollIntoView({ behavior: "smooth", block: "center" });
    }
}


