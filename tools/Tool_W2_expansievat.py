import math


def calculate_prepressure(st_height):
    static_prepressure = st_height * 0.1 + 0.3
    return math.ceil(round(static_prepressure * 2, 10)) / 2


def build_pressure_range_diagram(
    static_height_m,
    prepressure_bar,
    endpressure_bar,
    expansion_volume,
):
    plot_left, plot_top = 96, 28
    plot_right, plot_bottom = 670, 300
    plot_height = plot_bottom - plot_top
    static_pressure_bar = max(float(static_height_m), 0) * 0.1
    safety_pressure_bar = endpressure_bar + 0.5
    pressure_lines = [
        ("p0", static_pressure_bar, "#0d6efd", ""),
        ("p1", prepressure_bar, "#20a779", ""),
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

    fill_y = y_coordinate(prepressure_bar)
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
        "fill_pressure_bar": prepressure_bar,
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
                              round(expansion_volume,1), Temp_aanvoer, Temp_retour,round(einddruk,1) ,input_sys_inhoud, round(sys_inhoud), round(st_height, 1),CV_volume_norm,locatie_toggle, round(einddruk + 0.5, 1)]
        
    return expansievat_output