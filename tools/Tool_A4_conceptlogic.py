from django.shortcuts import redirect

SYSTEM_SCORE_BASE = {
    "ALL_ELECTRIC_WATER": 0,
    "HYBRID_RETROFIT": 0,
    "AIR_BASED_COMFORT": 0,
    "SMART_BUILDING": 0,
    "PROCESS_SYSTEM": 0,
}

QUESTIONS = {
    "start": {
        "text": "Wat is de situatie van het gebouw?",
        "options": [
            {
                "value": "nieuwbouw",
                "label": "Nieuwbouw - maximale ontwerpvrijheid",
                "next": "q_function",
            },
            {
                "value": "renovatie",
                "label": "Renovatie - rekening houden met bestaande situatie",
                "next": "q_function",
            },
        ],
    },

    "q_function": {
        "text": "Welke gebouwfunctie wordt ontworpen?",
        "options": [
            {
                "value": "woning",
                "label": "Woning / appartementen",
                "next": "q_ambition",
            },
            {
                "value": "kantoor",
                "label": "Kantoor / commerciële utiliteit",
                "next": "q_ambition",
            },
            {
                "value": "zorg",
                "label": "Zorggebouw",
                "next": "q_ambition",
            },
            {
                "value": "industrie",
                "label": "Industrie / procesomgeving",
                "next": "q_ambition",
            },
        ],
    },

    "q_ambition": {
        "text": "Wat is de belangrijkste ontwerpprioriteit?",
        "options": [
            {
                "value": "energie",
                "label": "Minimaal energiegebruik",
                "next": "q_source",
            },
            {
                "value": "comfort",
                "label": "Maximaal gebruikerscomfort",
                "next": "q_source",
            },
            {
                "value": "flexibiliteit",
                "label": "Flexibel gebouw voor toekomstig gebruik",
                "next": "q_source",
            },
            {
                "value": "kosten",
                "label": "Optimale investering",
                "next": "q_source",
            },
        ],
    },

    "q_source": {
        "text": "Welke energiebronnen zijn beschikbaar?",
        "options": [
            {
                "value": "bodem",
                "label": "Bodemenergie / WKO beschikbaar",
                "next": "q_heat",
            },
            {
                "value": "buitenlucht",
                "label": "Buitenlucht als bron",
                "next": "q_heat",
            },
            {
                "value": "warmtenet",
                "label": "Warmtenet beschikbaar",
                "next": "q_heat",
            },
            {
                "value": "onbekend",
                "label": "Nog onbekend",
                "next": "q_heat",
            },
        ],
    },

    "q_heat": {
        "text": "Welke verwarmingsstrategie past het beste?",
        "options": [
            {
                "value": "water",
                "label": "Watergedragen systeem (vloer/radiator/plafond)",
                "next": "q_cooling",
            },
            {
                "value": "air",
                "label": "Luchtgedragen systeem",
                "next": "q_cooling",
            },
            {
                "value": "hybrid",
                "label": "Combinatie water en lucht",
                "next": "q_cooling",
            },
        ],
    },

    "q_cooling": {
        "text": "Welke koelstrategie is gewenst?",
        "options": [
            {
                "value": "none",
                "label": "Geen actieve koeling",
                "next": "q_ventilation",
            },
            {
                "value": "comfort",
                "label": "Comfortkoeling",
                "next": "q_ventilation",
            },
            {
                "value": "process",
                "label": "Proceskoeling",
                "next": "q_ventilation",
            },
        ],
    },

    "q_ventilation": {
        "text": "Welke ventilatiestrategie past?",
        "options": [
            {
                "value": "natural",
                "label": "Natuurlijke ventilatie",
                "next": "q_control",
            },
            {
                "value": "decentral",
                "label": "Decentrale WTW-units",
                "next": "q_control",
            },
            {
                "value": "lbk",
                "label": "Centrale luchtbehandelingskast",
                "next": "q_control",
            },
        ],
    },

    "q_control": {
        "text": "Welk niveau van gebouwregeling is gewenst?",
        "options": [
            {
                "value": "basic",
                "label": "Basisregeling",
                "next": "q_energy",
            },
            {
                "value": "gbs",
                "label": "GBS / GBA",
                "next": "q_energy",
            },
            {
                "value": "smart",
                "label": "Smart Building met EMS",
                "next": "q_energy",
            },
        ],
    },

    "q_energy": {
        "text": "Welke energiecomponenten zijn gewenst?",
        "options": [
            {
                "value": "pv",
                "label": "PV-installatie",
                "next": "end",
            },
            {
                "value": "pv_storage",
                "label": "PV + batterij",
                "next": "end",
            },
            {
                "value": "smart",
                "label": "PV + EMS + energieoptimalisatie",
                "next": "end",
            },
        ],
    },
}

MAX_STEPS = len(QUESTIONS)

CONCEPTS = {

    "ALL_ELECTRIC_WATER": {
        "name": "All-electric watergedragen klimaatconcept",
        "description": (
            "Een laagtemperatuurconcept met warmtepomp, "
            "watergedragen distributie en duurzame energieopwekking."
        ),
        "systems": {

            "verwarming": {
                "opwekking": [
                    "Warmtepomp",
                    "Bodemenergie / WKO"
                ],
                "distributie": [
                    "LT waternet"
                ],
                "afgifte": [
                    "Vloerverwarming",
                    "Klimaatplafond"
                ]
            },

            "koeling": {
                "opwekking": [
                    "Passieve koeling WKO"
                ],
                "distributie": [
                    "Koud water"
                ],
                "afgifte": [
                    "Klimaatplafond",
                    "Vloerkoeling"
                ]
            },

            "ventilatie": {
                "opwekking": [
                    "Centrale LBK"
                ],
                "distributie": [
                    "Luchtkanalen"
                ],
                "afgifte": [
                    "VAV-systemen",
                    "Roosters"
                ]
            },

            "energie": {
                "opwekking": [
                    "PV-installatie",
                    "EMS-koppeling"
                ]
            },

            "regeling": [
                "GBS",
                "Zoneregeling"
            ]
        }
    },

    "HYBRID_RETROFIT": {
        "name": "Hybride renovatieconcept",
        "description": (
            "Flexibel concept waarbij bestaande installaties "
            "worden gecombineerd met nieuwe technieken."
        ),
        "systems": {

            "verwarming": {
                "opwekking": [
                    "Hybride warmtepomp",
                    "Bestaande ketel"
                ],
                "distributie": [
                    "Bestaand waternet"
                ],
                "afgifte": [
                    "Radiatoren",
                    "Vloerverwarming"
                ]
            },

            "koeling": {
                "opwekking": [
                    "Splitunits",
                    "Reversibele warmtepomp"
                ],
                "distributie": [
                    "Koudemiddelcircuit"
                ],
                "afgifte": [
                    "Binnenunits"
                ]
            },

            "ventilatie": {
                "opwekking": [
                    "Decentrale WTW"
                ],
                "distributie": [
                    "Lokale luchtkanalen"
                ],
                "afgifte": [
                    "Gevelunits"
                ]
            },

            "regeling": [
                "Ruimteregeling",
                "GBS-koppeling mogelijk"
            ]
        }
    },

    "AIR_BASED_COMFORT": {
        "name": "Luchtgedragen comfortconcept",
        "description": (
            "Integraal luchtconcept met centrale luchtbehandeling "
            "voor verwarmen, koelen en ventileren."
        ),
        "systems": {

            "verwarming": {
                "opwekking": [
                    "Warmtepomp",
                    "LBK-verwarmingsbatterij"
                ],
                "distributie": [
                    "Luchtkanalen"
                ],
                "afgifte": [
                    "Inblaasroosters"
                ]
            },

            "koeling": {
                "opwekking": [
                    "Koelmachine",
                    "Warmtepomp"
                ],
                "distributie": [
                    "Lucht"
                ],
                "afgifte": [
                    "VAV-systemen"
                ]
            },

            "ventilatie": {
                "opwekking": [
                    "Comfort-LBK",
                    "WTW"
                ],
                "distributie": [
                    "Kanaalsysteem"
                ],
                "afgifte": [
                    "Inductieroosters"
                ]
            },

            "regeling": [
                "CO₂-regeling",
                "GBS"
            ]
        }
    },

    "SMART_BUILDING": {
        "name": "Smart Building integraal concept",
        "description": (
            "Volledig geïntegreerd gebouw waarbij installaties "
            "samenwerken via GBS, EMS en energiemonitoring."
        ),
        "systems": {

            "energie": {
                "opwekking": [
                    "PV",
                    "PVT",
                    "Batterijopslag"
                ]
            },

            "regeling": [
                "GBS",
                "EMS",
                "Energiemonitoring",
                "Predictive Control"
            ]
        }
    },

    "PROCESS_SYSTEM": {
        "name": "Industrieel procesklimaatconcept",
        "description": (
            "Robuust systeem voor gebouwen met specifieke "
            "procescondities en kritische klimaateisen."
        ),
        "systems": {

            "ventilatie": {
                "opwekking": [
                    "Proces-LBK"
                ],
                "distributie": [
                    "Proceskanalen"
                ],
                "afgifte": [
                    "Proceslucht"
                ]
            },

            "regeling": [
                "Drukregeling",
                "Vochtregeling",
                "Procesmonitoring"
            ]
        }
    }

}

SCORING_RULES = {

        "start": {
            "nieuwbouw": {
                "ALL_ELECTRIC_WATER": 4,
                "SMART_BUILDING": 2,
            },
            "renovatie": {
                "HYBRID_RETROFIT": 5,
                "AIR_BASED_COMFORT": 1,
            },
        },

        "q_function": {
            "woning": {
                "ALL_ELECTRIC_WATER": 4,
            },
            "kantoor": {
                "AIR_BASED_COMFORT": 4,
                "SMART_BUILDING": 3,
            },
            "zorg": {
                "AIR_BASED_COMFORT": 4,
                "SMART_BUILDING": 2,
            },
            "industrie": {
                "PROCESS_SYSTEM": 8,
            },
        },

        "q_ambition": {
            "energie": {
                "ALL_ELECTRIC_WATER": 4,
                "SMART_BUILDING": 2,
            },
            "comfort": {
                "AIR_BASED_COMFORT": 3,
            },
            "flexibiliteit": {
                "SMART_BUILDING": 4,
            },
            "kosten": {
                "HYBRID_RETROFIT": 3,
            },
        },

        "q_source": {
            "bodem": {
                "ALL_ELECTRIC_WATER": 5,
            },
            "buitenlucht": {
                "ALL_ELECTRIC_WATER": 2,
                "HYBRID_RETROFIT": 2,
            },
            "warmtenet": {
                "ALL_ELECTRIC_WATER": 2,
            },
        },

        "q_heat": {
            "water": {
                "ALL_ELECTRIC_WATER": 5,
            },
            "air": {
                "AIR_BASED_COMFORT": 5,
            },
            "hybrid": {
                "HYBRID_RETROFIT": 4,
            },
        },

        "q_cooling": {
            "comfort": {
                "AIR_BASED_COMFORT": 2,
                "SMART_BUILDING": 1,
            },
            "process": {
                "PROCESS_SYSTEM": 5,
            },
        },

        "q_ventilation": {
            "lbk": {
                "AIR_BASED_COMFORT": 4,
            },
            "decentral": {
                "HYBRID_RETROFIT": 4,
            },
            "natural": {
                "HYBRID_RETROFIT": 1,
            },
        },

        "q_control": {
            "gbs": {
                "SMART_BUILDING": 4,
            },
            "smart": {
                "SMART_BUILDING": 7,
            },
        },

        "q_energy": {
            "pv": {
                "ALL_ELECTRIC_WATER": 2,
            },
            "pv_storage": {
                "SMART_BUILDING": 4,
            },
            "smart": {
                "SMART_BUILDING": 6,
            },
        },
}

def handle_tool_request(request):

    session = request.session

    answers = session.setdefault("answers", {})

    current_question = session.get(
        "current_question",
        "start"
    )

    if request.method == "POST":

        answers, current_question = _handle_post(
            request,
            session,
            answers,
            current_question,
        )

    return _decide_flow(
        session,
        answers,
        current_question,
    )



def _handle_post(
    request,
    session,
    answers,
    current_question,
):

    question_id = request.POST.get("question_id")
    answer = request.POST.get("answer")

    if not question_id:
        return answers, current_question

    if not answer:
        return answers, current_question

    answers[question_id] = answer

    session["answers"] = answers

    question = QUESTIONS.get(question_id)

    if not question:
        return answers, None

    next_question = None

    for option in question["options"]:

        if option["value"] == answer:

            next_question = option["next"]
            break

    session["current_question"] = next_question

    session.modified = True

    return answers, next_question


def _decide_flow(session, answers, current_q):
    if (
        not current_q
        or current_q == "end"
        or len(answers) >= MAX_STEPS
    ):
        result = evaluate(answers)

        session.pop("current_question", None)

        return {
            "is_result": True,
            "result": result,
            "answers": answers,
        }

    question = QUESTIONS.get(current_q)

    if not question:
        result = evaluate(answers)

        return {
            "is_result": True,
            "result": result,
            "answers": answers,
        }

    progress = int(
        (len(answers) / MAX_STEPS) * 100
    )

    return {
        "is_result": False,
        "question": question,
        "question_id": current_q,
        "step": len(answers),
        "total_steps": MAX_STEPS,
        "progress": progress,
    }


def _empty_state():
    return {
        "is_result": False,
        "question": QUESTIONS["start"],
        "question_id": "start",
        "step": 0,
        "total_steps": MAX_STEPS,
        "progress": 0,
    }

def evaluate(answers):

    score = SYSTEM_SCORE_BASE.copy()

    for question, answer in answers.items():

        question_scores = SCORING_RULES.get(
            question,
            {},
        )

        answer_scores = question_scores.get(
            answer,
            {},
        )

        for concept, points in answer_scores.items():

            score[concept] += points

    max_score = max(score.values())

    best_concepts = [

        concept

        for concept, value in score.items()

        if value == max_score

    ]

    primary = best_concepts[0]

    return build_result(
        primary=primary,
        score=score,
        answers=answers,
        ties=best_concepts,
    )

def build_result(
    primary,
    score,
    answers,
    ties,
):

    concept = CONCEPTS[primary]

    systems = _build_systems(
        concept["systems"]
    )

    ranked_scores = sorted(
        score.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    max_score = max(score.values())

    score_percentages = {

        name: round(
            (value / max_score) * 100
        )

        for name, value in score.items()

    }

    
    score_data = []

    for name, value in ranked_scores:

        score_data.append({
            "concept": CONCEPTS[name]["name"],
            "score": value,
            "percentage": score_percentages[name],
        })

    alternatives = [

        CONCEPTS[name]["name"]

        for name, _ in ranked_scores

        if name != primary

    ]

    warnings = _build_warnings(
        answers
    )

    score_text = ", ".join(

        f"{CONCEPTS[name]['name']} ({value})"

        for name, value in ranked_scores

    )

    return {

        "primary_concept": concept["name"],

        "systems": systems,

        "score": score,

        "score_percentage": score_percentages,

        "score_data": score_data,

        "alternatives": alternatives,

        "warnings": warnings,

        "ties": ties,

        "explanations": [

            concept["description"],

            f"Voorkeursconcept: {concept['name']}",

            f"Scoreverdeling: {score_text}",

        ],

    }

def _build_systems(data):

    systems = {
        "opwekking": [],
        "distributie": [],
        "afgifte": [],
        "regeling": [],
    }

    for section in (
        "verwarming",
        "koeling",
        "ventilatie",
    ):

        section_data = data.get(section)

        if not section_data:
            continue

        systems["opwekking"].extend(
            section_data.get(
                "opwekking",
                []
            )
        )

        systems["distributie"].extend(
            section_data.get(
                "distributie",
                []
            )
        )

        systems["afgifte"].extend(
            section_data.get(
                "afgifte",
                []
            )
        )

    systems["regeling"].extend(
        data.get("regeling", [])
    )

    if "energie" in data:

        systems["opwekking"].extend(
            data["energie"].get(
                "opwekking",
                []
            )
        )

    for key in systems:

        systems[key] = list(
            dict.fromkeys(
                systems[key]
            )
        )

    return systems

def _build_warnings(answers):

    warnings = []

    if answers.get("start") == "renovatie":

        warnings.append(
            "Controleer bestaande afgiftesystemen en beschikbare installatieruimte."
        )

    if answers.get("q_source") == "onbekend":

        warnings.append(
            "Beschikbare energiebron nog onbekend. Conceptkeuze later opnieuw valideren."
        )

    if answers.get("q_cooling") == "process":

        warnings.append(
            "Proceskoeling vraagt aanvullende dimensionering buiten standaard comfortinstallaties."
        )

    return warnings