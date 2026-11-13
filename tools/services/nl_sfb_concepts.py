from tools.models import ConceptSfbLink, InstallatieConcept, SfbClass


DEFAULT_CONCEPTS = {
    "Ventilator": {
        "synoniemen": (
            "ventilatoren, afzuigventilator, toevoerventilator, "
            "ventilatie-unit, mechanische ventilatie"
        ),
        "toelichting": (
            "De classificatie hangt af van lokale of centrale ventilatie."
        ),
        "links": {
            "57.21": "werktuigbouwkundig",
            "57.31": "werktuigbouwkundig",
        },
    },
    "Warmtepomp": {
        "synoniemen": (
            "warmtepompen, hybride warmtepomp, lucht-waterwarmtepomp, "
            "grondwarmtepomp, heat pump"
        ),
        "toelichting": "",
        "links": {"55.21": "werktuigbouwkundig"},
    },
    "Radiator": {
        "synoniemen": (
            "radiatoren, convector, convectoren, paneelradiator"
        ),
        "toelichting": "",
        "links": {"56.81": "werktuigbouwkundig"},
    },
    "Stopcontact": {
        "synoniemen": (
            "stopcontacten, wandcontactdoos, wandcontactdozen, contactdoos"
        ),
        "toelichting": (
            "Generieke wisselstroom-aansluitpunten; controleer bijzondere "
            "of specifieke aansluitingen afzonderlijk."
        ),
        "links": {"62.12": "elektrotechnisch"},
    },
    "Toilet": {
        "synoniemen": "wc, watercloset, toiletpot, closet, spoeltoilet",
        "toelichting": "",
        "links": {"74.11": "bouwkundig"},
    },
    "Lichtarmatuur": {
        "synoniemen": "lichtarmaturen, armatuur, armaturen, lamp, ledlamp",
        "toelichting": "",
        "links": {"63.21": "verlichting"},
    },
    "Noodverlichting": {
        "synoniemen": (
            "noodarmatuur, noodarmaturen, vluchtwegverlichting, "
            "noodverlichtingsarmatuur"
        ),
        "toelichting": (
            "Omvat de armaturen en, waar van toepassing, de centrale "
            "noodverlichtingsunit."
        ),
        "links": {
            "63.22": "verlichting",
            "61.11": "elektrotechnisch",
        },
    },
    "Zonnepaneel": {
        "synoniemen": (
            "zonnepanelen, pv-paneel, pv-panelen, pv, fotovoltaisch paneel"
        ),
        "toelichting": "",
        "links": {"61.15": "elektrotechnisch"},
    },
    "Rookmelder": {
        "synoniemen": "rookmelders, rookdetector, brandmelder, brandmelders",
        "toelichting": "",
        "links": {"65.11": "beveiliging"},
    },
    "Beveiligingscamera": {
        "synoniemen": (
            "camera, camerasysteem, cctv, bewakingscamera, videobewaking"
        ),
        "toelichting": "",
        "links": {"65.23": "beveiliging"},
    },
    "Toegangscontrole": {
        "synoniemen": (
            "toegangspas, toegangslezer, paslezer, toegangsbeveiliging"
        ),
        "toelichting": "",
        "links": {"65.22": "beveiliging"},
    },
}


def seed_default_concepts():
    """Create the initial searchable concepts without overwriting admin edits."""
    for name, defaults in DEFAULT_CONCEPTS.items():
        concept, _ = InstallatieConcept.objects.get_or_create(
            naam=name,
            defaults={
                "synoniemen": defaults["synoniemen"],
                "toelichting": defaults["toelichting"],
            },
        )

        for code, role in defaults["links"].items():
            sfb_class = SfbClass.objects.get(code=code)
            ConceptSfbLink.objects.get_or_create(
                concept=concept,
                sfb=sfb_class,
                rol=role,
            )
