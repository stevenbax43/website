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
    const searchStatus = searchZone.querySelector("#search-status");
    const searchUrl = searchZone.dataset.searchUrl;
    if (!searchInput || !resultsSection || !cardsContainer || !searchStatus || !searchUrl) return;

    let abortController = null;
    let debounceTimeout = null;

    searchInput.addEventListener("input", () => {
        const query = searchInput.value.trim();

        window.clearTimeout(debounceTimeout);
        if (abortController) abortController.abort();

        if (query.length < 2) {
            hideResults();
            searchStatus.textContent = "";
            return;
        }

        searchStatus.textContent = "Zoeken...";
        debounceTimeout = window.setTimeout(() => search(query), 250);
    });

    async function search(query) {
        abortController = new AbortController();
        try {
            const response = await fetch(`${searchUrl}?q=${encodeURIComponent(query)}`,
                { signal: abortController.signal }
            );
            if (!response.ok) {
                throw new Error(`Zoeken is mislukt (HTTP ${response.status}).`);
            }

            const data = await response.json();
            if (searchInput.value.trim() !== query) return;
            if (!data.routes || Object.keys(data.routes).length === 0) {
                hideResults();
                searchStatus.textContent = "Geen passende NL-SfB-classificaties gevonden.";
                return;
            }

            renderResults(data, query);
            searchStatus.textContent = "";

        } catch (err) {
            if (err.name === "AbortError") return;
            console.error("NL-SfB zoeken mislukt:", err);
            hideResults();
            searchStatus.textContent = "Zoeken is niet gelukt. Probeer het later opnieuw.";
        }
    }

    function hideResults() {
        resultsSection.classList.add("d-none");
        cardsContainer.replaceChildren();
        if (contextExplanation) contextExplanation.classList.add("d-none");
    }

    function renderResults(data, query) {
        resultsSection.classList.remove("d-none");
        cardsContainer.replaceChildren();
        if (contextExplanation) contextExplanation.classList.add("d-none");

        const contextCode = detectContextFromQuery(query);
        let hasUncertain = false;

        for (const [route, items] of Object.entries(data.routes)) {
            if (!Array.isArray(items) || items.length === 0) continue;

            const uncertain = items.filter(item => item.uncertain === true);
            const resolved = contextCode
                ? uncertain.find(item => item.code === contextCode)
                : null;
            const selectedItems = uncertain.length > 1 && resolved
                ? [resolved]
                : items.slice(0, 5);
            hasUncertain = hasUncertain || (uncertain.length > 1 && !resolved);

            selectedItems.forEach(item => {
                cardsContainer.appendChild(createScopeCard(route, item));
            });
        }

        if (hasUncertain && contextExplanation) {
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

    const button = document.createElement("button");
    button.type = "button";
    button.className = "card h-100 search-card w-100 text-start";
    button.dataset.nlsfbCode = item.code;
    button.setAttribute("aria-label", `Open NL-SfB ${item.code}: ${item.omschrijving}`);

    const body = document.createElement("div");
    body.className = "card-body";

    const header = document.createElement("div");
    header.className = "d-flex justify-content-between align-items-start";

    const title = document.createElement("h6");
    title.className = "mb-1";
    title.textContent = titleMap[route] || route;

    const badge = document.createElement("span");
    badge.className = `badge ${scopeClassMap[item.scope] || "bg-light text-dark"}`;
    badge.textContent = item.scope || "onbekend";
    header.append(title, badge);

    const description = document.createElement("div");
    description.className = "mt-2";
    const code = document.createElement("strong");
    code.textContent = `NL-SfB ${item.code}`;
    const text = document.createElement("span");
    text.className = "text-muted";
    text.textContent = item.omschrijving;
    description.append(code, document.createElement("br"), text);

    body.append(header, description);
    button.append(body);
    button.addEventListener("click", () => openAndHighlightNlSfb(item.code));
    col.append(button);
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
    if (!code) return [];
    if (code.endsWith("-")) return [code];

    const parts = [code.charAt(0) + "-"];
    const separatorIndex = code.indexOf(".");

    if (separatorIndex === -1) {
        parts.push(code);
        return [...new Set(parts)];
    }

    const baseCode = code.slice(0, separatorIndex);
    parts.push(baseCode);
    const suffix = code.slice(separatorIndex + 1);
    for (let length = 1; length <= suffix.length; length += 1) {
        parts.push(`${baseCode}.${suffix.slice(0, length)}`);
    }

    return [...new Set(parts)];
}

function enableNlSfbClicks(scope) {
    scope.querySelectorAll("tr[data-nlsfb]").forEach(row => {
        if (row.dataset.bound) return;
        row.dataset.bound = "true";
        row.tabIndex = 0;
        row.setAttribute("role", "button");
        row.setAttribute("aria-expanded", "false");

        row.addEventListener("click", async event => {
            event.stopPropagation();
            await toggleNlSfbRow(row, row.dataset.nlsfb);
        });
        row.addEventListener("keydown", async event => {
            if (event.key !== "Enter" && event.key !== " ") return;
            event.preventDefault();
            await toggleNlSfbRow(row, row.dataset.nlsfb);
        });
    });
}

const nlSfbCache = {};

async function fetchChildren(code) {
    if (nlSfbCache[code]) return nlSfbCache[code];

    const response = await fetch(
        `/tools/nl-sfb/nlsfb/children/${encodeURIComponent(code)}/`
    );
    if (!response.ok) {
        throw new Error(`NL-SfB-subklassen laden mislukt (HTTP ${response.status}).`);
    }

    const children = await response.json();
    nlSfbCache[code] = children;
    return children;
}

async function toggleNlSfbRow(row, code) {
    if (row.nextElementSibling?.classList.contains("nlsfb-children")) {
        row.nextElementSibling.remove();
        row.classList.remove("table-active");
        row.setAttribute("aria-expanded", "false");
        return;
    }

    try {
        const children = await fetchChildren(code);
        if (!children.length) return;

        row.classList.add("table-active");
        row.setAttribute("aria-expanded", "true");

        const childRow = document.createElement("tr");
        childRow.classList.add("nlsfb-children");

        const cell = document.createElement("td");
        cell.colSpan = 2;
        const wrapper = document.createElement("div");
        wrapper.className = "ps-4";
        const table = document.createElement("table");
        table.className = "table table-sm table-hover mb-0";
        const tbody = document.createElement("tbody");

        children.forEach(child => {
            const childItem = document.createElement("tr");
            childItem.dataset.nlsfb = child.code;

            const codeCell = document.createElement("td");
            codeCell.style.width = "140px";
            const strong = document.createElement("strong");
            strong.textContent = child.code;
            codeCell.append(strong);

            const descriptionCell = document.createElement("td");
            descriptionCell.textContent = child.omschrijving;
            childItem.append(codeCell, descriptionCell);
            tbody.append(childItem);
        });

        table.append(tbody);
        wrapper.append(table);
        cell.append(wrapper);
        childRow.append(cell);
        row.after(childRow);
        enableNlSfbClicks(childRow);
    } catch (error) {
        console.error("NL-SfB-subklassen laden mislukt:", error);
    }
}

async function openAndHighlightNlSfb(code) {
    const path = getNlSfbPath(code);

    document.querySelectorAll(".nlsfb-highlight")
        .forEach(element => element.classList.remove("nlsfb-highlight"));

    let targetRow = null;
    for (const step of path) {
        const rows = document.querySelectorAll(
            `tr[data-nlsfb="${step}"]`
        );
        if (!rows.length) continue;

        const row = rows[rows.length - 1];
        if (!row.nextElementSibling?.classList.contains("nlsfb-children")) {
            await toggleNlSfbRow(row, step);
        }

        if (step === code) targetRow = row;
    }

    if (targetRow) {
        targetRow.classList.add("nlsfb-highlight");
        targetRow.scrollIntoView({ behavior: "smooth", block: "center" });
        targetRow.focus({ preventScroll: true });
    }
}
