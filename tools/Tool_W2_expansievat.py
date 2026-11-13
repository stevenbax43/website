import math


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
):
    plot_left, plot_top = 96, 28
    plot_right, plot_bottom = 670, 300
    plot_height = plot_bottom - plot_top
    static_pressure_bar = max(float(static_height_m), 0) * 0.1
    safety_pressure_bar = endpressure_bar + 0.5
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
            lowest_temperature = 0
            highest_temperature = 0

        input_sys_inhoud = int(float(request.POST.get('sys_inhoud') or 0))
        einddruk, st_height, vermogen = map(float,[
            request.POST.get('einddruk'),
            request.POST.get('st_height'),
            request.POST.get('vermogen') or 0,
        ])
        
                                                                     
        CV_keuze = int(request.POST.get('CVInstallatie') or 4)
        system_volume_unknown = request.POST.get('sys_inhoud_onbekend') == 'on'
        
        #bepaal einddruk 
        locatie_toggle = bool(request.POST.get('locatieToggle'))
        
        if not locatie_toggle: #als de circulatiepomp in de retourleiding zit
            einddruk = einddruk - 0.4

        voordruk = calculate_prepressure(st_height)
        if not cooling_mode and voordruk >= einddruk:
            raise InvalidPressureRange(
                f"De berekende voordruk ({voordruk:.1f} bar) is niet lager dan "
                f"de effectieve einddruk ({einddruk:.1f} bar). Verlaag de "
                "statische hoogte of verhoog de einddruk."
            )

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
        
        #bepaal inhoud vat op basis van input waarde
        VolumeExpansionPercentage = [(25, 0.35),(30, 0.43),(35, 0.63),(40, 0.75),(45, 0.96),(50, 1.18),(55, 1.42),(60, 1.68),(70, 2.25),(80, 2.89),(90, 3.58),(100, 4.34),(110, 5.16)]
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
            closest_index_exp = min(range(len(VolumeExpansionPercentage)), key=lambda i: abs(VolumeExpansionPercentage[i][0] - Temp_average))
            expansion_percentage = VolumeExpansionPercentage[closest_index_exp][1]
        expansion_volume = round(
            (expansion_percentage / 100) * sys_inhoud,
            1,
        )

        based_on_voor = (
            '*Berekend op basis van statische hoogte '
            '(0,1 bar per meter + 0,3 bar veiligheidsmarge; afgerond naar '
            'boven op stappen van 0,5 bar)'
        )
        if cooling_mode:
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
        else:
            lowest_operating_pressure = voordruk
            raw_nuttig_effect = (einddruk - voordruk) / (einddruk + 1)
        if raw_nuttig_effect <= 0:
            raise InvalidPressureRange(
                "De einddruk moet hoger zijn dan de laagste bedrijfsdruk."
            )
        sizing_effect = min(raw_nuttig_effect, 0.63) if cooling_mode else raw_nuttig_effect
        nuttig_effect = round(sizing_effect, 3)
        if nuttig_effect <= 0:
            raise InvalidPressureRange(
                "Het drukverschil is te klein om een geldig expansievat te "
                "berekenen. Verhoog de einddruk."
            )
        reserve_factor = 1.5 if cooling_mode else 1.25
        bruto_vessel = round(
            (expansion_volume * reserve_factor) / sizing_effect,
            1,
        )
        volume_advies = math.ceil(bruto_vessel / 5) * 5
        
        
        reserve_volume = (
            math.ceil(expansion_volume * 0.5 * 10) / 10
            if cooling_mode
            else round(expansion_volume * 0.25, 1)
        )
        expansievat_output = [Temp_average, nuttig_effect, bruto_vessel, volume_advies, voordruk, based_on_sys, based_on_voor, expansion_percentage,
                              round(expansion_volume,1), Temp_aanvoer, Temp_retour,round(einddruk,1) ,input_sys_inhoud, round(sys_inhoud), round(st_height, 1),CV_volume_norm,locatie_toggle, round(einddruk + 0.5, 1), calculation_mode, glycol_percentage, lowest_temperature, highest_temperature, reserve_volume, lowest_operating_pressure]
        
    return expansievat_output