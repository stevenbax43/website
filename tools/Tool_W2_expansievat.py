import math


def calculate_prepressure(st_height):
    static_prepressure = st_height * 0.1 + 0.3
    return math.ceil(round(static_prepressure * 2, 10)) / 2


def build_pressure_height_diagram(st_height, prepressure_bar, endpressure_bar):
    height = max(float(st_height), 0)
    plot_left, plot_top = 82, 24
    plot_width, plot_height = 650, 276
    x_max = height if height > 0 else 1
    pressure_drop_per_meter = 9810
    pressure_lines = [
        ("p0", prepressure_bar, "#0d6efd", ""),
        ("pv", prepressure_bar + 0.3, "#20a779", ""),
        ("pe", endpressure_bar, "#fd7e14", ""),
        ("safety", 3, "#dc3545", "8 5"),
    ]

    series = []
    for key, pressure_bar, color, dash in pressure_lines:
        start_pa = pressure_bar * 100000
        end_pa = start_pa - pressure_drop_per_meter * height
        series.append({
            "key": key,
            "color": color,
            "dash": dash,
            "start_pa": start_pa,
            "end_pa": end_pa,
        })

    all_pressures = [
        pressure
        for item in series
        for pressure in (item["start_pa"], item["end_pa"])
    ]
    pressure_min = min(0, min(all_pressures))
    pressure_max = max(0, max(all_pressures))
    raw_step = max((pressure_max - pressure_min) / 6, 1)
    magnitude = 10 ** math.floor(math.log10(raw_step))
    normalized_step = raw_step / magnitude
    step_factor = 1 if normalized_step <= 1 else 2 if normalized_step <= 2 else 5 if normalized_step <= 5 else 10
    tick_step = step_factor * magnitude
    axis_min = math.floor(pressure_min / tick_step) * tick_step
    axis_max = math.ceil(pressure_max / tick_step) * tick_step
    if axis_max == axis_min:
        axis_max = axis_min + tick_step

    def y_coordinate(pressure_pa):
        return plot_top + (axis_max - pressure_pa) / (axis_max - axis_min) * plot_height

    for item in series:
        end_x = plot_left + height / x_max * plot_width
        item["start_x"] = plot_left
        item["start_y"] = y_coordinate(item["start_pa"])
        item["end_x"] = end_x
        item["end_y"] = y_coordinate(item["end_pa"])
        item["path"] = (
            f"M {item['start_x']} {item['start_y']:.1f} "
            f"L {item['end_x']:.1f} {item['end_y']:.1f}"
        )

    y_ticks = []
    tick = axis_min
    while tick <= axis_max:
        y_ticks.append({
            "value": tick,
            "y": y_coordinate(tick),
            "label": f"{int(tick):,}".replace(",", "."),
        })
        tick += tick_step

    x_tick_values = (
        [height * index / 4 for index in range(5)] if height > 0 else [0]
    )
    x_ticks = [{
        "x": plot_left + value / x_max * plot_width,
        "label": f"{value:.1f}".rstrip("0").rstrip("."),
    } for value in x_tick_values]

    return {
        "height": height,
        "height_label": f"{height:g}",
        "plot_left": plot_left,
        "plot_top": plot_top,
        "plot_right": plot_left + plot_width,
        "plot_bottom": plot_top + plot_height,
        "series": series,
        "y_ticks": y_ticks,
        "x_ticks": x_ticks,
    }


def expansievat(request): 
    Temp_aanvoer, Temp_retour, Temp_average, input_sys_inhoud, expansion_volume,CV_volume_norm = 0,0,0,0,0,0
    einddruk, st_height, nuttig_effect, bruto_vessel, volume_advies, vermogen, voordruk =0,0,0,0,0,0,0
    based_on_voor, based_on_sys = '',''
    locatie_toggle = False
    VolumeExpansionPercentage, CVInstallatieValues,expansievat_output= [], [], []
    if request.method =='POST':
        
        Temp_aanvoer, Temp_retour = map(int, [
            request.POST.get('temp_aanvoer'),
            request.POST.get('temp_retour'),
        ])
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
        
        if locatie_toggle == False: #als de circulatiepomp in de retourleiding zit
            einddruk = einddruk - 0.4
        else:
            einddruk = einddruk
        #bepaal inhoud vat op basis van vermogen en CV-keuze
        CVInstallatieValues = [(0,5.2),(1,5.5),(2,6.9),(3,8.8),(4,10.0),(5,12.0),(6,20.0),(7,18.5),(8,25.8)]
        closest_index_CV = min(range(len(CVInstallatieValues)), key=lambda i: abs(CVInstallatieValues[i][0] - CV_keuze))
        CV_volume_norm = CVInstallatieValues[closest_index_CV][1]
        calc_sys_inhoud = CV_volume_norm* vermogen 
        if system_volume_unknown:
            sys_inhoud = calc_sys_inhoud
            based_on_sys = 'Vermogen en CV-afgifte'
        else:
            sys_inhoud = input_sys_inhoud
            based_on_sys = 'Ingevoerde Vsys'
        
        #bepaal inhoud vat op basis van input waarde
        Temp_average = int((Temp_aanvoer + Temp_retour) /2)
        VolumeExpansionPercentage = [(25, 0.35),(30, 0.43),(35, 0.63),(40, 0.75),(45, 0.96),(50, 1.18),(55, 1.42),(60, 1.68),(70, 2.25),(80, 2.89),(90, 3.58),(100, 4.34),(110, 5.16)]
        closest_index_exp = min(range(len(VolumeExpansionPercentage)), key=lambda i: abs(VolumeExpansionPercentage[i][0] - Temp_average))
        expansion_percentage = VolumeExpansionPercentage[closest_index_exp][1]
        expansion_volume = round(((expansion_percentage/100) * sys_inhoud),2)

        voordruk = calculate_prepressure(st_height)
        based_on_voor = (
            '*Berekend op basis van statische hoogte '
            '(0,1 bar per meter + 0,3 bar veiligheidsmarge; afgerond naar '
            'boven op stappen van 0,5 bar)'
        )
        nuttig_effect = round(
            ((einddruk + 1) - (voordruk + 1)) / (einddruk + 1),
            2,
        )
        bruto_vessel = round((expansion_volume * 1.25) / nuttig_effect, 1)
        volume_advies = math.ceil(bruto_vessel / 5) * 5
        
        
        expansievat_output = [Temp_average, nuttig_effect, bruto_vessel, volume_advies, voordruk, based_on_sys, based_on_voor, expansion_percentage,
                              round(expansion_volume,1), Temp_aanvoer, Temp_retour,round(einddruk,1) ,input_sys_inhoud, round(sys_inhoud), round(st_height, 1),CV_volume_norm,locatie_toggle ]
        
    return expansievat_output