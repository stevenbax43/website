import math
from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape

from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class InvalidPressureRange(ValueError):
    pass


class InvalidCoolingInputs(ValueError):
    pass


COOLING_GLYCOL_PERCENTAGES = (0, 10, 20, 30, 40, 50)
COOLING_EXPANSION_TABLE = {
    10: (0.04, 0.35, 0.67, 0.89, 1.31, 1.63),
    20: (0.18, 0.50, 0.82, 1.04, 1.46, 1.78),
    30: (0.43, 0.75, 1.07, 1.29, 1.71, 2.03),
    40: (0.79, 1.11, 1.43, 1.65, 2.07, 2.39),
    50: (1.21, 1.53, 1.85, 2.07, 2.49, 2.81),
    60: (1.71, 2.03, 2.35, 2.57, 2.99, 3.31),
    70: (2.25, 2.60, 2.92, 3.14, 3.56, 3.88),
    80: (2.89, 3.22, 3.54, 3.76, 4.18, 4.52),
    90: (3.58, 3.91, 4.23, 4.45, 4.87, 5.19),
    100: (4.35, 4.63, 4.95, 5.17, 5.59, 5.90),
}
FLAMCO_FLEXCON_NOMINAL_VOLUMES_L = (
    2, 4, 8, 12, 18, 25, 35, 50, 80, 110, 140, 200, 300, 425, 600, 800,
    1000,
)
FLAMCO_FLEXCON_PREPRESSURE_OPTIONS_BAR = {
    2: (0.5,),
    4: (0.5,),
    8: (0.5,),
    12: (0.5, 1.0),
    18: (0.5, 1.0, 1.5),
    25: (0.5, 1.0, 1.5),
    35: (0.5, 1.0, 1.5),
    50: (0.5, 1.0, 1.5),
    80: (0.5, 1.0, 1.5),
    110: (0.5, 1.0, 1.5, 2.0, 2.5),
    140: (0.5, 1.0, 1.5, 2.0, 2.5, 3.0),
    200: (0.5, 1.0, 1.5, 2.0, 2.5, 3.0),
    300: (0.5, 1.0, 1.5, 2.0, 2.5, 3.0),
    425: (0.5, 1.0, 1.5, 2.0, 2.5, 3.0),
    600: (0.5, 1.0, 1.5, 2.0, 2.5, 3.0),
    800: (1.0, 1.5, 2.0, 2.5, 3.0),
    1000: (1.5, 2.0, 2.5, 3.0),
}


def water_density_kg_m3(temperature):
    if not 0 <= temperature <= 100:
        raise ValueError("De watertemperatuur moet tussen 0 °C en 100 °C liggen.")
    return 1000 * (
        1
        - ((temperature + 288.9414)
           / (508929.2 * (temperature + 68.12963)))
        * (temperature - 3.9863) ** 2
    )


def calculate_nen_expansion_vessel(
    system_volume_l,
    expansion_volume_l,
    prepressure_bar,
    endpressure_bar,
    safety_pressure_bar=3.0,
):
    if system_volume_l <= 0 or expansion_volume_l <= 0:
        raise InvalidPressureRange(
            "De systeeminhoud en het expansievolume moeten groter zijn dan nul."
        )
    if safety_pressure_bar > 10:
        raise InvalidPressureRange(
            "De Flamco Flexcon-vatmaten in de catalogus zijn beschikbaar tot "
            "10 bar werkdruk. Controleer een vat met een hogere drukklasse."
        )

    useful_effect = (endpressure_bar - prepressure_bar) / (endpressure_bar + 1)
    if useful_effect <= 0:
        raise InvalidPressureRange(
            "De einddruk moet hoger zijn dan de voordruk."
        )

    for nominal_volume_l in FLAMCO_FLEXCON_NOMINAL_VOLUMES_L:
        if nominal_volume_l <= 80 and safety_pressure_bar > 3:
            continue
        if prepressure_bar not in FLAMCO_FLEXCON_PREPRESSURE_OPTIONS_BAR[
            nominal_volume_l
        ]:
            continue
        if nominal_volume_l <= 15:
            reserve_volume_l = nominal_volume_l * 0.2
        else:
            reserve_volume_l = max(system_volume_l * 0.005, 3)
        max_working_pressure_bar = (
            3 if nominal_volume_l <= 80
            else 6 if safety_pressure_bar <= 6
            else 10
        )

        minimum_nominal_volume_l = (
            expansion_volume_l + reserve_volume_l
        ) / useful_effect
        if nominal_volume_l < minimum_nominal_volume_l:
            continue

        initial_pressure_bar = (
            (expansion_volume_l + reserve_volume_l)
            * (prepressure_bar + 1)
            * (endpressure_bar + 1)
            / (nominal_volume_l * (endpressure_bar - prepressure_bar))
            - 1
        )
        if prepressure_bar <= initial_pressure_bar + 0.3:
            continue

        return {
            "minimum_nominal_volume_l": minimum_nominal_volume_l,
            "nominal_volume_l": nominal_volume_l,
            "reserve_volume_l": reserve_volume_l,
            "initial_pressure_bar": initial_pressure_bar,
            "useful_effect": useful_effect,
            "max_working_pressure_bar": max_working_pressure_bar,
        }

    raise InvalidPressureRange(
        "Er is geen passende Flexcon-vatmaat gevonden die voldoet aan de "
        "minimale inhoud en de voordrukvoorwaarde uit NEN-EN 12828."
    )


def cooling_expansion_percentage(temperature, glycol_percentage):
    if glycol_percentage not in COOLING_GLYCOL_PERCENTAGES:
        raise InvalidCoolingInputs(
            "Kies voor het glycolpercentage een waarde van 0% tot 50% "
            "in stappen van 10%."
        )
    if not 10 <= temperature <= 100:
        raise InvalidCoolingInputs(
            "De Flamco-koeltabel is beschikbaar van 10 °C tot 100 °C."
        )

    lower_temperature = int(temperature // 10) * 10
    lower_temperature = min(max(lower_temperature, 10), 90)
    upper_temperature = lower_temperature + 10
    lower_value = COOLING_EXPANSION_TABLE[lower_temperature][
        COOLING_GLYCOL_PERCENTAGES.index(glycol_percentage)
    ]
    upper_value = COOLING_EXPANSION_TABLE[upper_temperature][
        COOLING_GLYCOL_PERCENTAGES.index(glycol_percentage)
    ]
    fraction = (temperature - lower_temperature) / 10
    return lower_value + (upper_value - lower_value) * fraction


def calculate_prepressure(st_height):
    static_prepressure = st_height * 0.1 + 0.3
    return math.ceil(round(static_prepressure * 2, 10)) / 2


def build_pressure_range_diagram(
    static_height_m,
    prepressure_bar,
    endpressure_bar,
    expansion_volume,
    working_pressure_bar=None,
    safety_pressure_bar=None,
):
    plot_left, plot_top = 96, 28
    plot_right, plot_bottom = 670, 300
    plot_height = plot_bottom - plot_top
    static_pressure_bar = max(float(static_height_m), 0) * 0.1
    safety_pressure_bar = (
        endpressure_bar + 0.5
        if safety_pressure_bar is None
        else safety_pressure_bar
    )
    pv_pressure_bar = (
        prepressure_bar if working_pressure_bar is None else working_pressure_bar
    )
    pressure_lines = [
        ("p0", static_pressure_bar, "#0d6efd", ""),
        ("p1", pv_pressure_bar, "#20a779", ""),
        ("pe", endpressure_bar, "#fd7e14", ""),
        ("safety", safety_pressure_bar, "#dc3545", "8 5"),
    ]
    pressure_max = max(line[1] for line in pressure_lines)
    raw_step = max(pressure_max / 6, 0.01)
    magnitude = 10 ** math.floor(math.log10(raw_step))
    normalized_step = raw_step / magnitude
    step_factor = (
        1 if normalized_step <= 1
        else 2 if normalized_step <= 2
        else 5 if normalized_step <= 5
        else 10
    )
    tick_step = step_factor * magnitude
    axis_min = 0
    axis_max = max(tick_step, math.ceil(pressure_max / tick_step) * tick_step)

    def y_coordinate(pressure_bar):
        return plot_top + (axis_max - pressure_bar) / (axis_max - axis_min) * plot_height

    series = [{
        "key": key,
        "pressure_bar": pressure_bar,
        "y": y_coordinate(pressure_bar),
        "color": color,
        "dash": dash,
    } for key, pressure_bar, color, dash in pressure_lines]
    y_ticks = []
    tick = axis_min
    while tick <= axis_max + tick_step / 1000:
        y_ticks.append({
            "y": y_coordinate(tick),
            "label": f"{tick:.2f}".rstrip("0").rstrip(".").replace(".", ","),
        })
        tick += tick_step

    working_pressure_bar = pv_pressure_bar
    fill_y = y_coordinate(working_pressure_bar)
    end_y = y_coordinate(endpressure_bar)
    return {
        "plot_left": plot_left,
        "plot_top": plot_top,
        "plot_right": plot_right,
        "plot_bottom": plot_bottom,
        "plot_width": plot_right - plot_left,
        "series": series,
        "y_ticks": y_ticks,
        "fill_area_top": min(fill_y, end_y),
        "fill_area_height": abs(fill_y - end_y),
        "fill_pressure_bar": working_pressure_bar,
        "endpressure_bar": endpressure_bar,
        "expansion_volume": expansion_volume,
    }

def expansievat(request): 
    Temp_aanvoer, Temp_retour, Temp_average, input_sys_inhoud, expansion_volume,CV_volume_norm = 0,0,0,0,0,0
    einddruk, st_height, nuttig_effect, bruto_vessel, volume_advies, vermogen, voordruk =0,0,0,0,0,0,0
    based_on_voor, based_on_sys = '',''
    locatie_toggle = False
    VolumeExpansionPercentage, CVInstallatieValues,expansievat_output= [], [], []
    if request.method =='POST':
        calculation_mode = request.POST.get('calculation_mode', 'heating')
        cooling_mode = calculation_mode == 'cooling'
        if calculation_mode not in ('heating', 'cooling'):
            raise InvalidCoolingInputs("Kies verwarming of koeling.")

        if cooling_mode:
            try:
                lowest_temperature = float(request.POST.get('cooling_min_temp', ''))
                highest_temperature = float(request.POST.get('cooling_max_temp', ''))
                glycol_percentage = float(request.POST.get('glycol_percentage', ''))
            except (TypeError, ValueError):
                raise InvalidCoolingInputs(
                    "Vul de laagste en hoogste temperatuur en het glycolpercentage in."
                )
            if lowest_temperature >= highest_temperature:
                raise InvalidCoolingInputs(
                    "De hoogste temperatuur moet hoger zijn dan de laagste temperatuur."
                )
            if glycol_percentage not in COOLING_GLYCOL_PERCENTAGES:
                raise InvalidCoolingInputs(
                    "Kies een glycolpercentage van 0% tot 50% in stappen van 10%."
                )
            Temp_aanvoer = highest_temperature
            Temp_retour = lowest_temperature
            Temp_average = (lowest_temperature + highest_temperature) / 2
        else:
            Temp_aanvoer, Temp_retour = map(int, [
                request.POST.get('temp_aanvoer'),
                request.POST.get('temp_retour'),
            ])
            Temp_average = int((Temp_aanvoer + Temp_retour) / 2)
            glycol_percentage = 0
            try:
                lowest_temperature = float(request.POST.get('temp_min', '10'))
            except (TypeError, ValueError):
                raise InvalidPressureRange(
                    "Vul de laagste mogelijke systeemtemperatuur in."
                )
            highest_temperature = 0

        input_sys_inhoud = int(float(request.POST.get('sys_inhoud') or 0))
        einddruk, st_height, vermogen = map(float,[
            request.POST.get('einddruk'),
            request.POST.get('st_height'),
            request.POST.get('vermogen') or 0,
        ])
        
                                                                     
        CV_keuze = int(request.POST.get('CVInstallatie') or 4)
        system_volume_unknown = request.POST.get('sys_inhoud_onbekend') == 'on'
        
        safety_pressure_bar = einddruk
        locatie_toggle = bool(request.POST.get('locatieToggle'))

        voordruk = calculate_prepressure(st_height)

        #bepaal inhoud vat op basis van vermogen en CV-keuze
        CVInstallatieValues = [(0,5.2),(1,5.5),(2,6.9),(3,8.8),(4,10.0),(5,12.0),(6,20.0),(7,18.5),(8,25.8)]
        closest_index_CV = min(range(len(CVInstallatieValues)), key=lambda i: abs(CVInstallatieValues[i][0] - CV_keuze))
        CV_volume_norm = CVInstallatieValues[closest_index_CV][1]
        calc_sys_inhoud = CV_volume_norm* vermogen 
        if cooling_mode and system_volume_unknown:
            raise InvalidCoolingInputs(
                "Voor de Flamco-koelmethode is de werkelijke systeeminhoud nodig. "
                "Vul deze in en schakel 'Systeeminhoud onbekend' uit."
            )
        if system_volume_unknown:
            sys_inhoud = calc_sys_inhoud
            based_on_sys = 'Vermogen en CV-afgifte'
        else:
            sys_inhoud = input_sys_inhoud
            based_on_sys = 'Ingevoerde Vsys'
        if sys_inhoud <= 0:
            raise InvalidPressureRange(
                "Vul een systeeminhoud groter dan nul liter in."
            )
        
        #bepaal inhoud vat op basis van input waarde
        if cooling_mode:
            expansion_percentage = (
                cooling_expansion_percentage(
                    highest_temperature,
                    glycol_percentage,
                )
                - cooling_expansion_percentage(
                    lowest_temperature,
                    glycol_percentage,
                )
            )
            if expansion_percentage <= 0:
                raise InvalidCoolingInputs(
                    "De Flamco-tabel geeft voor deze temperaturen geen positieve uitzetting."
                )
        else:
            if Temp_retour > Temp_aanvoer:
                raise InvalidPressureRange(
                    "De retourtemperatuur mag niet hoger zijn dan de maximale "
                    "bedrijfstemperatuur."
                )
            if not 0 <= lowest_temperature < Temp_aanvoer <= 100:
                raise InvalidPressureRange(
                    "De laagste systeemtemperatuur moet lager zijn dan de "
                    "maximale bedrijfstemperatuur (maximaal 100 °C)."
                )
            density_min = water_density_kg_m3(lowest_temperature)
            density_max = water_density_kg_m3(Temp_aanvoer)
            expansion_percentage = (
                density_min / density_max - 1
            ) * 100
        expansion_volume = (expansion_percentage / 100) * sys_inhoud

        based_on_voor = (
            '*Berekend op basis van statische hoogte '
            '(0,1 bar per meter + 0,3 bar veiligheidsmarge; afgerond naar '
            'boven op stappen van 0,5 bar)'
        )
        if cooling_mode:
            if not locatie_toggle:
                einddruk -= 0.4
            lowest_operating_pressure = voordruk + 0.5
            einddruk -= 0.5
            if einddruk <= lowest_operating_pressure:
                raise InvalidPressureRange(
                    "De einddruk moet minimaal 0,5 bar boven de voordruk liggen "
                    "en 0,5 bar onder de insteldruk van het veiligheidsventiel."
                )
            fill_fraction = (
                (lowest_operating_pressure - voordruk)
                / (lowest_operating_pressure + 1)
            )
            rest_factor = 1 - fill_fraction
            raw_nuttig_effect = (
                (einddruk - lowest_operating_pressure)
                / (einddruk + 1)
                * rest_factor
            )
            based_on_voor = (
                "Flamco-koelmethode: laagste bedrijfsdruk 0,5 bar boven de "
                "voordruk; einddruk 0,5 bar onder de veiligheidsventielinstelling"
            )
            nuttig_effect = round(min(raw_nuttig_effect, 0.63), 3)
            reserve_factor = 1.5
            bruto_vessel = round(
                (expansion_volume * reserve_factor) / min(raw_nuttig_effect, 0.63),
                1,
            )
            volume_advies = math.ceil(bruto_vessel / 5) * 5
            reserve_volume = math.ceil(expansion_volume * 0.5 * 10) / 10
        else:
            einddruk = safety_pressure_bar - 0.5
            if not locatie_toggle:
                einddruk -= 0.4
            if voordruk >= einddruk:
                raise InvalidPressureRange(
                    f"De berekende voordruk ({voordruk:.1f} bar) is niet lager "
                    f"dan de effectieve einddruk ({einddruk:.1f} bar). Verlaag "
                    "de statische hoogte of verhoog de insteldruk."
                )
            lowest_operating_pressure = voordruk
            vessel_sizing = calculate_nen_expansion_vessel(
                sys_inhoud,
                expansion_volume,
                voordruk,
                einddruk,
                safety_pressure_bar,
            )
            nuttig_effect = round(vessel_sizing["useful_effect"], 3)
            bruto_vessel = round(
                vessel_sizing["minimum_nominal_volume_l"],
                1,
            )
            volume_advies = vessel_sizing["nominal_volume_l"]
            reserve_volume = round(vessel_sizing["reserve_volume_l"], 1)
            initial_pressure = vessel_sizing["initial_pressure_bar"]
            based_on_voor = (
                "NEN-EN 12828 D.2: einddruk 0,5 bar onder de "
                "veiligheidsventielinstelling; bij een retourpomp is 0,4 bar "
                "drukverschil verrekend"
            )
        reported_safety_pressure = (
            einddruk + 0.5 if cooling_mode else safety_pressure_bar
        )
        expansievat_output = [
            Temp_average,
            nuttig_effect,
            bruto_vessel,
            volume_advies,
            voordruk,
            based_on_sys,
            based_on_voor,
            round(expansion_percentage, 2),
            round(expansion_volume, 1),
            Temp_aanvoer,
            Temp_retour,
            round(einddruk, 1),
            input_sys_inhoud,
            round(sys_inhoud),
            round(st_height, 1),
            CV_volume_norm,
            locatie_toggle,
            round(reported_safety_pressure, 1),
            calculation_mode,
            glycol_percentage,
            lowest_temperature,
            highest_temperature,
            reserve_volume,
            lowest_operating_pressure,
        ]
        if not cooling_mode:
            expansievat_output.extend([
                reserve_volume,
                bruto_vessel,
                round(initial_pressure, 2),
                volume_advies,
                vessel_sizing["max_working_pressure_bar"],
                Temp_aanvoer > 90 or Temp_retour > 70,
                round(density_min, 2),
                round(density_max, 2),
            ])
        
    return expansievat_output


def generate_pdf_expansion_vessel(request):
    if request.method != "POST":
        return HttpResponse("Ongeldig verzoek.", status=400)

    project_name = request.POST.get("project_name", "").strip()[:80]
    project_number = request.POST.get("project_number", "").strip()[:40]
    project_description = request.POST.get("project_description", "").strip()[:500]
    if not project_name or not project_number or not project_description:
        return HttpResponse(
            "Vul de projectnaam, het projectnummer en de omschrijving in.",
            status=400,
        )

    try:
        result = expansievat(request)
    except (InvalidPressureRange, InvalidCoolingInputs, TypeError, ValueError) as error:
        return HttpResponse(str(error), status=400)
    if not result:
        return HttpResponse("Er zijn geen berekeningsresultaten om te exporteren.", status=400)

    cooling_mode = result[18] == "cooling"
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title="Tool W2 - Expansievat",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "W2Title",
        parent=styles["Title"],
        textColor=colors.HexColor("#174a73"),
        alignment=0,
        spaceAfter=4,
    )
    heading_style = ParagraphStyle(
        "W2Heading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#174a73"),
        fontSize=12,
        leading=15,
        spaceBefore=10,
        spaceAfter=5,
    )
    body_style = ParagraphStyle(
        "W2Body",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
    )

    def paragraph(value, style=body_style):
        safe_value = escape(str(value if value not in (None, "") else "-"))
        return Paragraph(safe_value.replace("\n", "<br/>"), style)

    def format_number(value, decimals=2):
        return f"{float(value):.{decimals}f}".rstrip("0").rstrip(".").replace(".", ",")

    def make_table(rows, widths):
        table = Table(
            [[paragraph(label), paragraph(value)] for label, value in rows],
            colWidths=widths,
            hAlign="LEFT",
        )
        table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f8")),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d6dde3")),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        return table

    mode_name = "Koelinstallatie" if cooling_mode else "Verwarmingsinstallatie"
    input_rows = [
        ("Installatietype", mode_name),
        ("Systeeminhoud (Vsys)", f"{format_number(result[13], 1)} L"),
        ("Berekeningsbasis systeeminhoud", result[5]),
        ("Statische hoogte", f"{format_number(result[14], 1)} m"),
        ("Insteldruk veiligheidsventiel (Ps)", f"{format_number(result[17], 1)} bar"),
    ]
    if cooling_mode:
        input_rows.extend([
            ("Laagste temperatuur", f"{format_number(result[10], 1)} °C"),
            ("Hoogste temperatuur", f"{format_number(result[9], 1)} °C"),
            ("Glycol", f"{format_number(result[19], 1)}%"),
        ])
    else:
        input_rows.extend([
            ("Laagste systeemtemperatuur (Tmin)", f"{format_number(result[20], 1)} °C"),
            ("Maximale bedrijfstemperatuur (Tmax)", f"{format_number(result[9], 1)} °C"),
            ("Retourtemperatuur", f"{format_number(result[10], 1)} °C"),
            ("Pomp in vertrekleiding", "Ja" if result[16] else "Nee (retourleiding)"),
        ])

    result_rows = [
        ("Expansievolume (Vexp)", f"{format_number(result[8], 1)} L"),
        ("Voordruk (P0)", f"{format_number(result[4], 1)} bar"),
        ("Einddruk (Pfin)", f"{format_number(result[11], 1)} bar"),
        ("Nuttig effect (ne)", format_number(result[1], 3)),
    ]
    if cooling_mode:
        result_rows.extend([
            ("Expansiepercentage", f"{format_number(result[7], 2)}%"),
            ("Reserve (50% van Vexp)", f"{format_number(result[22], 1)} L"),
            ("Bruto vatvolume", f"{format_number(result[2], 1)} L"),
            ("Geadviseerd vatvolume", f"{format_number(result[3], 1)} L"),
        ])
    else:
        result_rows.extend([
            ("Expansiecoefficient (e)", f"{format_number(result[7], 2)}%"),
            ("Dichtheid bij Tmin", f"{format_number(result[30], 2)} kg/m3"),
            ("Dichtheid bij Tmax", f"{format_number(result[31], 2)} kg/m3"),
            ("Minimale waterreserve (Vwr,min)", f"{format_number(result[22], 1)} L"),
            ("Minimum nominaal volume (VN,min)", f"{format_number(result[2], 1)} L"),
            ("Geadviseerde Flexcon-vatmaat", f"{format_number(result[3], 1)} L"),
            ("Maximale werkdruk vat", f"{format_number(result[28], 1)} bar"),
            ("Berekende initiele druk (pini)", f"{format_number(result[26], 2)} bar"),
        ])

    story = [
        Paragraph("Tool W2 - Inhoud expansievat", title_style),
        paragraph(f"{mode_name} | Gemaakt op {datetime.now().strftime('%d-%m-%Y %H:%M')}"),
        Spacer(1, 8),
        make_table([
            ("Projectnaam", project_name),
            ("Projectnummer", project_number),
            ("Omschrijving", project_description),
        ], [36 * mm, 138 * mm]),
        Paragraph("Invoer", heading_style),
        make_table(input_rows, [74 * mm, 100 * mm]),
        Paragraph("Resultaten", heading_style),
        make_table(result_rows, [74 * mm, 100 * mm]),
        Paragraph("Rekenmethode", heading_style),
        paragraph(
            "NEN-EN 12828, bijlage D.2; vatmaat op basis van de aangeleverde "
            "Flamco Flexcon-catalogus uit 2015."
            if not cooling_mode else
            "Afzonderlijke Flamco-koelmethode; de verwarmingsberekening volgens "
            "NEN-EN 12828 D.2 is niet van toepassing."
        ),
    ]
    if not cooling_mode:
        story.extend([
            Spacer(1, 4),
            paragraph(
                "e = rho(Tmin) / rho(Tmax) - 1; Vexp = Vsys x e; "
                "ne = (Pfin - P0) / (Pfin + 1); "
                "VN,min = (Vexp + Vwr,min) / ne."
            ),
        ])
    if not cooling_mode and result[29]:
        story.extend([
            Spacer(1, 6),
            paragraph(
                "Let op: volgens de Flamco-catalogus is bij een aanvoertemperatuur "
                "boven 90 °C of een retourtemperatuur boven 70 °C een voorschakelvat nodig."
            ),
        ])
    document.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Tool_W2_expansievat.pdf"'
    return response