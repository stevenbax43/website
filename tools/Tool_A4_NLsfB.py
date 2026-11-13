# tools/services/tool_A5.py

from pathlib import Path
from typing import Dict

import pandas as pd
from django.conf import settings

from tools.models import SfbClass


# ============================================================
# IMPORTFUNCTIE
# ============================================================

def import_nl_sfb_classification():
    """
    Leest NL-SfB Tabel 1 (Elementenmethode 2005) uit Excel
    en vult SfbClass inclusief parent-relaties.

    Idempotent: veilig opnieuw uit te voeren.
    """

    excel_path = (
        Path(settings.BASE_DIR)
        / "tools"
        / "static"
        / "tools"
        / "files"
        / "TOOL_A4_NL_sfB.xlsx"
    )

    df = (
        pd.read_excel(
            excel_path,
            sheet_name="NL-SfB_Tabel 1",
            engine="openpyxl",
            dtype=str,
        )
        .fillna("")
    )

    # ─────────────────────────────────────────────
    # FASE 1 – records aanmaken / bijwerken
    # ─────────────────────────────────────────────

    sfb_cache: Dict[str, SfbClass] = {}

    for _, row in df.iterrows():

        code = str(row.get("Class-codenotatie", "")).strip()
        omschrijving = str(row.get("tekst_NL-SfB", "")).strip()

        # ✅ FILTER 1: lege of nan codes
        if not code or code.lower() == "nan":
            continue

        # ✅ FILTER 2: titelregel overslaan
        if omschrijving.lower().startswith("tabel 1"):
            continue

        sfb, _ = SfbClass.objects.update_or_create(
            code=code,
            defaults={
                "classificatie": str(
                    row.get("Classificatie", "")
                ).strip(),
                "taal": str(
                    row.get("Taal", "")
                ).strip(),
                "tabel": str(
                    row.get("Tabel", "")
                ).strip(),
                "code_tekst": str(
                    row.get("Class-tekstcodenotatie", "")
                ).strip(),
                "omschrijving": omschrijving,
            },
        )

        sfb_cache[code] = sfb

    # ─────────────────────────────────────────────
    # FASE 2 – parent-relaties leggen
    # ─────────────────────────────────────────────

    to_update = []

    for code, sfb in sfb_cache.items():

        parent_code = get_parent_code(code)

        new_parent = (
            sfb_cache.get(parent_code)
            if parent_code
            else None
        )

        if sfb.parent != new_parent:
            sfb.parent = new_parent
            to_update.append(sfb)

    if to_update:
        SfbClass.objects.bulk_update(
            to_update,
            ["parent"]
        )


# ============================================================
# HULPFUNCTIES
# ============================================================


def get_parent_code(code: str):
    """
    Bepaalt de parentcode binnen de NL-SfB boom.

    Voorbeelden:
        5-      -> None
        57      -> 5-
        57.3    -> 57
        57.31   -> 57.3
        57.311  -> 57.31
    """

    code = code.strip()

    # Hoofdstukniveau
    if code.endswith("-"):
        return None

    # Subniveau
    if "." in code:
        base_code, suffix = code.split(".", 1)
        if len(suffix) > 1:
            return f"{base_code}.{suffix[:-1]}"
        return base_code

    # Tweecijferige klasse
    if len(code) == 2 and code.isdigit():
        return f"{code[0]}-"

    return None


def get_class_by_code(code: str):
    """
    Haalt één NL-SfB klasse op.

    Retourneert:
        SfbClass object of None
    """

    return (
        SfbClass.objects
        .filter(code=code)
        .first()
    )


def get_children(code: str):
    """
    Geeft directe children van een NL-SfB code terug.
    """

    return (
        SfbClass.objects
        .filter(parent__code=code)
        .order_by("code")
    )