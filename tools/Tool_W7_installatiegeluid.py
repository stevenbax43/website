import math


OCTAVE_BANDS = (
    (63, -26),
    (125, -16),
    (250, -9),
    (500, -3),
    (1000, 0),
    (2000, 1),
    (4000, 1),
    (8000, -1),
)


def _number(value, label, minimum=None, maximum=None):
    if isinstance(value, bool):
        raise ValueError(f"{label} moet een getal zijn.")
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} moet een getal zijn.") from None
    if not math.isfinite(number):
        raise ValueError(f"{label} moet een eindig getal zijn.")
    if minimum is not None and number < minimum:
        raise ValueError(f"{label} moet minimaal {minimum} zijn.")
    if maximum is not None and number > maximum:
        raise ValueError(f"{label} mag maximaal {maximum} zijn.")
    return number


def logarithmic_sum(levels):
    if not isinstance(levels, list) or not 1 <= len(levels) <= 50:
        raise ValueError("Vul minimaal één en maximaal 50 geluidsniveaus in.")
    values = [_number(level, "Geluidsniveau", -200, 200) for level in levels]
    return 10 * math.log10(sum(10 ** (level / 10) for level in values))


def calculate_a_weighted_spectrum(levels):
    if not isinstance(levels, list) or len(levels) != len(OCTAVE_BANDS):
        raise ValueError("Vul voor elke octaafband een waarde in of laat deze leeg.")

    bands = []
    unweighted_levels = []
    weighted_levels = []
    for (frequency, correction), level in zip(OCTAVE_BANDS, levels):
        if level is None or level == "":
            continue
        level_db = _number(level, f"{frequency} Hz", -200, 200)
        level_a_db = level_db + correction
        unweighted_levels.append(level_db)
        weighted_levels.append(level_a_db)
        bands.append({
            "frequency_hz": frequency,
            "level_db": level_db,
            "correction_db": correction,
            "level_a_db": level_a_db,
        })

    if not weighted_levels:
        raise ValueError("Vul minimaal één octaafband in.")
    total_db = 10 * math.log10(
        sum(10 ** (level / 10) for level in unweighted_levels)
    )
    total_db_a = 10 * math.log10(
        sum(10 ** (level / 10) for level in weighted_levels)
    )
    return {"bands": bands, "total_db": total_db, "total_db_a": total_db_a}


def sound_pressure_level(sound_power_db, directivity_factor, distance_m):
    sound_power = _number(sound_power_db, "Geluidsvermogenniveau Lw", -200, 200)
    directivity = _number(directivity_factor, "Richtingscoëfficiënt Q", 0.000001, 100)
    distance = _number(distance_m, "Afstand r", 0.000001, 100000)
    return sound_power + 10 * math.log10(
        directivity / (4 * math.pi * distance ** 2)
    )


def equivalent_sound_level(level_a_db, operating_hours, assessment_hours):
    level = _number(level_a_db, "Geluidsdrukniveau Lp,A", -200, 200)
    operating = _number(operating_hours, "Bedrijfsduur Tb", 0.000001, 8760)
    assessment = _number(assessment_hours, "Beoordelingsperiode T0", 0.000001, 8760)
    if operating > assessment:
        raise ValueError("De bedrijfsduur Tb mag niet groter zijn dan T0.")
    return level + 10 * math.log10(operating / assessment)


def calculate(payload):
    if not isinstance(payload, dict):
        raise ValueError("Ongeldige invoer.")

    calculation = payload.get("calculation")
    if calculation == "sum":
        return {"total_db": logarithmic_sum(payload.get("levels"))}
    if calculation == "spectrum":
        return calculate_a_weighted_spectrum(payload.get("levels"))
    if calculation == "distance":
        return {
            "lp_db": sound_pressure_level(
                payload.get("lw_db"),
                payload.get("directivity_factor"),
                payload.get("distance_m"),
            )
        }
    if calculation == "equivalent":
        return {
            "laeq_db": equivalent_sound_level(
                payload.get("lp_a_db"),
                payload.get("operating_hours"),
                payload.get("assessment_hours"),
            )
        }
    raise ValueError("Onbekende berekening.")
