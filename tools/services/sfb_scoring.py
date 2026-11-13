import re
from typing import Set, Dict, List
from collections import defaultdict
from tools.models import SfbClass


# ============================================================
# 1. ROL-KEYWORDS (semantische interpretatie)
# ============================================================

ROLE_KEYWORDS: Dict[str, Set[str]] = {

    # Opwekking
    "opwekking": {
        "warmtepomp", "koelmachine", "chiller", "ketel", "cv-ketel", "wkk"
    },

    # Warmte / koude context
    "warmte": {
        "verwarming", "warmte", "cv",
        "radiator", "vloerverwarming", "ketel", "warmtepomp"
    },
    "koude": {
        "koeling", "koel", "koelinstallatie",
        "koelmachine", "chiller"
    },

    # Medium
    "lucht": {
        "lucht", "luchtbehandeling",
        "kanaal", "kanalen",
        "ventilator", "afzuig", "toevoer",
        "rwa"
    },
    "vloeistof": {
        "water", "glycol", "cv", "koelwater",
        "leiding", "leidingen",
        "pomp", "circulatiepomp", "hydrofoor",
        "inregelafsluiter", "regelafsluiter"
    },

    # Distributie
    "distributie": {
        "leiding", "leidingen",
        "kanaal", "kanalen",
        "afsluiter",
        "inregelafsluiter",
        "regelafsluiter",
        "balansventiel",
        "circulatiepomp"
    },

    # Actieve regeling (alleen bij motorisering)
    "actieve_regeling": {
        "regelklep",
        "motorregelklep",
        "gemotoriseerde regelafsluiter",
        "ventilator",
        "brandklep",
        "rookluik",
        "circulatiepomp",
        "overdrukinstallatie"
    },

    # Detectie / BMI
    "detectie": {
        "rookmelder", "brandmelder", "handbrandmelder",
        "detector", "sensor",
        "brandmeldinstallatie", "bmi"
    },

    # Veiligheidscontext
    "veiligheidscontext": {
        "brand", "rook",
        "brandklep", "rookluik",
        "rwa", "rookwarmteafvoer",
        "brandventilatie",
        "brandmeldinstallatie", "bmi"
    },

    # Verlichting (NL-SfB 63)
    "verlichting": {
        "verlichting", "licht", "armatuur", "lamp", "led",
        "noodverlichting", "vluchtwegverlichting",
        "lichtpunt", "downlight", "opbouwarmatuur", "inbouwarmatuur"
    },

    # Beveiliging (CCTV e.d.)
    "beveiliging": {
        "cctv", "camera", "camerasysteem",
        "videobewaking", "bewakingscamera",
        "toegangscontrole", "inbraak"
    },
    
# --------------------------------------------------
    # VASTE VOORZIENINGEN 70–76
    # --------------------------------------------------

    "vaste_verkeersvoorziening": {
        "bewegwijzering",
        "routebord",
        "verkeersbord",
        "markering",
        "hekwerk",
        "afscheiding",
    },

    "vaste_gebruikersvoorziening": {
        "meubilair",
        "kast",
        "tafel",
        "bank",
        "stoel",
        "lichtwering",
        "zonwering",
        "gordijn",
        "rolgordijn",
    },

    "keukenvoorziening": {
        "keuken",
        "keukenblok",
        "keukenmeubilering",
        "keukenvoorziening",
        "vaste keuken",
    },

    "sanitaire_voorziening": {
        "wc",
        "toilet",
        "sanitair",
        "urinoir",
        "wastafel",
        "wasbak",
        "closet",
        "spoeltoilet",
    },

    "onderhoudsvoorziening": {
        "onderhoudsvoorziening",
        "gevelonderhoud",
        "dakonderhoud",
        "valbeveiliging",
        "ankerpunt",
    },

    "opslagvoorziening": {
        "kast",
        "opslag",
        "berging",
        "stelling",
        "vaste opslag",
    },

}


# ============================================================
# 2. ROUTE → SCOPE
# ============================================================

ROUTE_SCOPE = {
    "werktuigbouwkundig": "installateur",
    "besturing": "installateur",
    "elektrotechnisch": "installateur",
    "beveiliging": "installateur",
    "brandveiligheid": "functioneel",
    "bouwkundig": "afstemming",
    "verlichting": "installateur",
    "communicatie": "installateur",
}

TECHNICAL_PARTS = {
    "afscheider",
    "afsluiter",
    "armatuur",
    "batterij",
    "brandklep",
    "brandmelder",
    "detector",
    "filter",
    "gasmeter",
    "heater",
    "hydrofoor",
    "kanaal",
    "klep",
    "koelbalk",
    "koelmachine",
    "leiding",
    "luchtkast",
    "luchtrooster",
    "luchtverhitter",
    "omvormer",
    "paneel",
    "pomp",
    "radiator",
    "regelaar",
    "regelklep",
    "rooster",
    "sensor",
    "transformator",
    "ventiel",
    "warmtepomp",
}
# ============================================================
# 3. TOKENISATIE
# ============================================================

def tokenize(text: str) -> Set[str]:
    return set(re.findall(r"[a-z]+", text.lower()))


def tokenize_search_term(term: str) -> Set[str]:
    tokens = tokenize(term)
    expanded = set(tokens)

    # sub-woorden herkennen (brandklep → brand + klep)
    for token in tokens:
        for words in ROLE_KEYWORDS.values():
            for w in words:
                if w in token:
                    expanded.add(w)

    return expanded


def determine_component_roles(tokens: Set[str]) -> Set[str]:
    roles: Set[str] = set()

    for role, words in ROLE_KEYWORDS.items():
        if tokens & words:
            roles.add(role)

    # Detectie impliceert altijd veiligheidscontext
    if "detectie" in roles:
        roles.add("veiligheidscontext")

    return roles


# ============================================================
# 4. NL‑SfB TEKSTUELE ZOEKING (50–90)
# ============================================================

def determine_route(sfb: SfbClass) -> str:
    code = sfb.code
    if code.startswith("59"):
        return "brandveiligheid"
    if code.startswith("65"):
        return "beveiliging"
    if code.startswith("64"):
        return "communicatie"
    if code.startswith("63"):
        return "verlichting"
    if code.startswith("58"):
        return "besturing"
    if code.startswith("6"):
        return "elektrotechnisch"
    if code.startswith("5"):
        return "werktuigbouwkundig"
    if code[0] in {"1", "2", "3", "4"}:
        return "bouwkundig"
    return "overig"


def search_sfb_by_text(tokens: Set[str]) -> Dict[str, List[dict]]:
    """
    Tekstuele zoeking in de volledige NL-SfB tabel.
    """

    #print("\n" + "=" * 60)
    #print("search_sfb_by_text draait")
    #print("TOKENS:", tokens)

    results: Dict[str, List[dict]] = defaultdict(list)

    for sfb in SfbClass.objects.all():

        search_text = (
            f"{sfb.omschrijving} {sfb.code_tekst}"
        )

        sfb_tokens = tokenize(search_text)

        overlap = set()

        for token in tokens:

            for sfb_token in sfb_tokens:

                match = (
                    token == sfb_token
                    or token == sfb_token.rstrip("s")
                    or (
                        token in TECHNICAL_PARTS
                        and (
                            sfb_token.endswith(token)
                            or token in sfb_token
                        )
                    )
                )

                if match:
                    overlap.add(token)

                    print(
                        f"MATCH FOUND | "
                        f"zoek='{token}' | "
                        f"sfb_token='{sfb_token}' | "
                        f"code={sfb.code}"
                    )

        if not overlap:
            continue

        score = round(len(overlap) / len(tokens), 3)

        route = determine_route(sfb)

        print(
            f"RESULT | "
            f"{sfb.code} | "
            f"{sfb.omschrijving} | "
            f"score={score}"
        )

        results[route].append({
            "code": sfb.code,
            "omschrijving": sfb.omschrijving,
            "score": score,
            "scope": ROUTE_SCOPE.get(route),
        })

    final: Dict[str, List[dict]] = {}

    for route, items in results.items():
        items.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        final[route] = [items[0]]

    print("FINAL:", final)

    return final

# ============================================================
# 5. SYSTEEMUITBREIDING (ROL → CORRECTIE / VERRIJKING)
# ============================================================

def expand_system_routes(roles: Set[str]) -> Dict[str, List[dict]]:
    """
    Semantische correcties en component-logica.
    Overschrijft waar nodig tekstuele NL‑SfB-resultaten.
    """
    result: Dict[str, List[dict]] = {}

    # Brand- en rookbeheersing
    if "actieve_regeling" in roles and "veiligheidscontext" in roles:
        result["werktuigbouwkundig"] = [{
            "code": "57.4",
            "omschrijving": "luchtbehandeling; distributie",
            "scope": "installateur"
        }]
        result["brandveiligheid"] = [{
            "code": "59.3",
            "omschrijving": "brandveiligheid; brandventilatieinstallatie",
            "scope": "functioneel"
        }]
        result["besturing"] = [{
            "code": "58.8",
            "omschrijving": "sturing brandbeheersing",
            "scope": "installateur"
        }]
        result["elektrotechnisch"] = [{
            "code": "61.3",
            "omschrijving": "elektrotechnische voeding",
            "scope": "installateur"
        }]
        result["bouwkundig"] = [{
            "code": "33",
            "omschrijving": "brandwerende doorvoeringen",
            "scope": "afstemming"
        }]
        return result

    # Detectie / BMI
    if "detectie" in roles:
        return {
            "beveiliging": [{
                "code": "65.1",
                "omschrijving": "brandmeldings- en ontruimingsinstallatie",
                "scope": "installateur"
            }],
            "besturing": [{
                "code": "58.8",
                "omschrijving": "koppeling BMI / GBS",
                "scope": "installateur"
            }],
            "elektrotechnisch": [{
                "code": "61.3",
                "omschrijving": "voeding en bekabeling",
                "scope": "installateur"
            }],
        }

    # Passieve distributie
    if "distributie" in roles and "vloeistof" in roles:
        return {
            "werktuigbouwkundig": [
                {
                    "code": "56",
                    "omschrijving": "verwarming; distributie",
                    "scope": "installateur",
                    "uncertain": True
                },
                {
                    "code": "55",
                    "omschrijving": "koeling; distributie",
                    "scope": "installateur",
                    "uncertain": True
                }
            ]
        }

    return result


# ============================================================
# 6. HOOFDFUNCTIE
# ============================================================

def analyse_search_term(term: str) -> Dict[str, List[dict]]:
    
    tokens = tokenize_search_term(term)
    roles = determine_component_roles(tokens)

    # A. NL‑SfB tabel (hoofdzakelijk hoofdstukken 50–90)
    base_routes = search_sfb_by_text(tokens)

    # B. Rol-gedreven correcties / uitbreidingen
    role_routes = expand_system_routes(roles)

    # C. Rollen winnen bij conflict
    for route, items in role_routes.items():
        base_routes[route] = items

    return base_routes
