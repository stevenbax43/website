import pandas as pd 
import numpy as np
import math, json, base64
from scipy.optimize import minimize_scalar
from io import BytesIO
from datetime import datetime
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle, Paragraph, Frame, Spacer


def MollierView(request): 
    # Defaults
    lines_RH = []
    lines_H = []
    calc_start_point = {}
    calc_points = [{} for _ in range(4)]  # One per possible step
    process_values = [[None] * 7 for _ in range(4)]
    process_names = [''] * 4  # Default empty names for 4 steps
    process_data = []
    active_steps = [1, 2, 3, 4]  # Handle process steps count (from POST)
    warning_message =  None
    #handle POST
    if request.method == 'POST':
         # Read active steps
        current_proces_raw = request.POST.get('currentProces', '')
        active_steps = [
            int(p) for p in current_proces_raw.split(',') if p.strip().isdigit()
        ]
        active_steps = [p for p in active_steps if 1 <= p <= 4]
         # Get process names
        for i in range(4):
            name = request.POST.get(f'inputproces{i+1}_name', '').strip()
            if len(name) > 15:
                name = name[:15]  # Truncate just in case
            process_names[i] = name if name else f'Proces {i}'
        # Step 3: Run Mollier calculations (uses POST data)
        mollier_render_output = MollierValues(request)
        if mollier_render_output:
            lines_RH = mollier_render_output.get("lines_RH", [])
            lines_H = mollier_render_output.get("lines_H", [])
            calc_start_point = mollier_render_output.get("calc_start_point", {})

            # Points per process step
            all_points = [
                mollier_render_output.get("calc_point_one", {}),
                mollier_render_output.get("calc_point_two", {}),
                mollier_render_output.get("calc_point_three", {}),
                mollier_render_output.get("calc_point_four", {}),
            ]
            for i in active_steps:
                calc_points[i - 1] = all_points[i - 1]

            # Step 4: Get all process values
            process_values_full = mollier_render_output.get("process_values", [[None] * 7 for _ in range(4)])
            for i in active_steps:
                process_values[i - 1] = process_values_full[i - 1] or [None] * 7

            # Step 5: Build final process_data
            for step in active_steps:
                index = step - 1
                process_data.append({
                    'step': step,
                    'name': process_names[index],
                    'values': process_values[index]
                })
            warning_message = mollier_render_output.get("warning", None)
    #outside the POST request:            
    mollierView_output = [lines_RH,lines_H,calc_start_point,calc_points,process_data,warning_message]
    return mollierView_output

def MollierValues(request):
    mollier_render_output = {}
    height_start, qv_start = 0, 0
    warning_message =  None
    if request.method == 'POST':
        # Parse general inputs
        height_start = safe_float(request.POST.get('Height_var'), 0)
        qv_start = safe_float(request.POST.get('qv_var'), 10000)
        pressure = 101325 + (1 - 2.25577e-5 * height_start) ** 5.256
        lines_RH, lines_H, df_enthalpy, C_values = mollier_graph(pressure)
              

        # Get start point variables and values
        var1 = request.POST.get('varStart1')
        var2 = request.POST.get('varStart2')
        val1 = safe_float(request.POST.get('StartInput1'))
        val2 = safe_float(request.POST.get('StartInput2'))
     
        result  = infer_Tdb_RH_from_any_two(var1, val1, var2, val2, pressure, C_values, lines_RH)
        if isinstance(result, tuple) and len(result) == 3:
            Tdb_start, RH_start, was_invalid = result
            if was_invalid:
                warning_message = "<strong>Waarschuwing</strong>: combinatie van waarden is niet geldig! Waarden zijn herberekend."
        else:
            Tdb_start, RH_start = result
        
        calc_start_point = calculate_mollier(Tdb_start, RH_start, qv_start, df_enthalpy, pressure, C_values, rho_prev=None, Tdb_100=None, x_100=None, qv_meng=None)
        
        # Helper function for each process step
        def handle_process(proces_name, calc_input_point, idx,func1, func2):
            if proces_name != 'selectProces':
                inputs = [safe_float(request.POST.get(f'Proces{idx}_value{i}_input', '')) for i in range(1, 10)]
                
                result = infer_Tdb_RH_from_proces(
                    calc_input_point, proces_name, func1, func2,
                    *inputs, pressure, C_values, lines_RH
                )

                Tdb, RH = result[0], result[1]
                Tdb_100 = result[2] if len(result) > 2 else None
                x_100 = result[3] if len(result) > 3 else None
                qv_meng = result[4] if len(result) > 4 else None
               
                calc_point = calculate_mollier(
                    Tdb, RH, calc_input_point[11], df_enthalpy,
                    pressure, C_values, calc_input_point[4], Tdb_100, x_100,qv_meng
                )

                step_values  = calculate_proces_values(calc_input_point, calc_point)
                return calc_point, step_values 
            else:
                return {}, {}

        # Process step inputs
        proces1 = request.POST.get('proces1')
        proces2 = request.POST.get('proces2')
        proces3 = request.POST.get('proces3')
        proces4 = request.POST.get('proces4')
        # Get shared functions
        funcs = {
            1: (request.POST.get('proces1_func'), request.POST.get('proces1_func2')),
            2: (request.POST.get('proces2_func'), request.POST.get('proces2_func2')),
            3: (request.POST.get('proces3_func'), request.POST.get('proces3_func2')),
            4: (request.POST.get('proces4_func'), request.POST.get('proces4_func2')),
        }
        # Execute steps
        calc_point_one, proces_values_one = handle_process(proces1, calc_start_point, 1,*funcs[1])
        calc_point_two, proces_values_two = handle_process(proces2, calc_point_one, 2,*funcs[2])
        calc_point_three, proces_values_three = handle_process(proces3, calc_point_two, 3, *funcs[3])
        calc_point_four, proces_values_four = handle_process(proces4, calc_point_three, 4,*funcs[4])

        # Assemble output
        mollier_render_output = {
            "lines_RH": lines_RH,
            "lines_H": lines_H,
            "calc_start_point": calc_start_point,
            "calc_point_one": calc_point_one,
            "calc_point_two": calc_point_two,
            "calc_point_three": calc_point_three,
            "calc_point_four": calc_point_four,
            "process_values": [proces_values_one, proces_values_two, proces_values_three, proces_values_four],
            "warning": warning_message,
        }

    return mollier_render_output

def mollier_graph(pBar=101325):
    #voor berekenen Tdb onder 0 graden Celsius
    C1,C2,C3,C4,C5,C6,C7 = -5.6745359e3, 6.3925247,-9.6778430e-3,6.2215701e-7,2.0747825e-9,-9.4840240e-13,4.1635019
    #voor berekenen Tdb boven 0 graden Celsius
    C8,C9,C10,C11,C12,C13 = -5.8002206e3,1.3914993,-4.8640239e-2, 4.1764768e-5, -1.4452093e-8, 6.5459673
    #voor berekenen dauwpunt:
    C14, C15, C16,C17,C18= 6.54, 14.526,0.7389, 0.09486,0.4569
    C_values = [0,C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13,C14,C15,C16,C17,C18]

    # create Relative Humidity lines
    Tdb_range = np.arange(-15, 41, 1)
    RH_range = np.arange(10,110,10)
    database_RH = np.zeros((len(RH_range), len(Tdb_range)))  # Initialize matrix with zeros 

    for i, RH in enumerate(RH_range):
        for j, Tdb in enumerate(Tdb_range):
            #formula below 0 degrees Celcius 
            part1 = 0.62198 * RH * calculate_saturated_vapor_pressure(Tdb, C_values)/100
            part2 = pBar - RH * calculate_saturated_vapor_pressure(Tdb, C_values)/100
            outcome = part1 / part2 * 1000
            database_RH[i, j] = outcome # outcome is calculated in [g/kg] watervapor [g] in one [kg] of air. 
    #make the numpy array an dataframe pandas 
    dataframe_RH = pd.DataFrame(database_RH.T, columns=RH_range, index=Tdb_range) #transpose database_RH 
    
    
    #create Enthalpy lines 
    H_range = np.arange(-10,95,5) # unit in [kJ/kG] 
    df_enthalpy = pd.DataFrame(H_range, columns=['H_range'])
    df_enthalpy['T_0'] = df_enthalpy['H_range']/1.006    # something weird in the formulas 
    df_enthalpy['T_100'] = [-13.1,-9.21,-5.75,-2.58,0.33,3.125,5.71,8.1,10.306,12.36,14.27,16.05,17.718,19.28,20.753,22.14,23.45,24.692,25.87,26.992,28.06] #wet-bulb temp
   

    #get the calculated [g/kg] from the 100% RH database
    RH_100 = database_RH[-1] #this is the 100% list
    df_enthalpy['RH_100_interpolated'] = [np.interp(T, Tdb_range, RH_100) for T in df_enthalpy['T_100']]
    #create list for chartdata in HTML 
    lines_RH = {
        'x_values': dataframe_RH.index.tolist(),  # X-axis values from 0 to 40
        'ten_percent': dataframe_RH.iloc[:, 0].tolist(), 
        'twenty_percent': dataframe_RH.iloc[:, 1].tolist(), 
        'thirty_percent': dataframe_RH.iloc[:, 2].tolist(), 
        'fourty_percent': dataframe_RH.iloc[:, 3].tolist(), 
        'fifty_percent': dataframe_RH.iloc[:, 4].tolist(), 
        'sixty_percent': dataframe_RH.iloc[:, 5].tolist(), 
        'seventy_percent': dataframe_RH.iloc[:, 6].tolist(), 
        'eighty_percent': dataframe_RH.iloc[:, 7].tolist(), 
        'ninety_percent': dataframe_RH.iloc[:, 8].tolist(), 
        'onehondered_percent': dataframe_RH.iloc[:, 9].tolist(), 
    }
    lines_H = {
        'x_values': df_enthalpy['H_range'].tolist(),
        'y2': df_enthalpy['RH_100_interpolated'].tolist(),
        'x1': df_enthalpy['T_0'].tolist(),
        'x2': df_enthalpy['T_100'].tolist(),   
    }
    return lines_RH, lines_H, df_enthalpy, C_values

def calculate_mollier(Tdb_var, RH_var, qv_prev, df_enthalpy, pressure=101325, C_values=None, rho_prev=None, Tdb_100=None, x_100=None,qv_meng=None):
    # Calculate extra parameters
    formatted_pBar = f"{pressure / 1000:.3f}"
    pws = calculate_saturated_vapor_pressure(Tdb_var, C_values)
    pv = RH_var/100 * pws
    x = calculate_humidity_ratio(pv, pressure) #g/kg is de abs. vochtigheid op basis van invoer
    
    Td = calculate_dew_point(pv,Tdb_var, C_values)
    H = calculate_enthalpy(Tdb_var,x)#(1006*Tdb_var+x*(2500.77+Tdb_var*1.82))/1000 # kJ/kG enthalpy op basis van invoer
    V = calculate_specific_volume(Tdb_var,x,pressure) # 0.2871* (Tdb_var+273.15)*(1+1.6078*x/1000)/(pBar/1000) #specific Volume (rho) op basis van invoer
    rho = 1/V # density (rho) op basis van invoer
    if qv_meng is not None: #als er een mengproces is, dan is qv_meng de nieuwe qv
        qv_proces = qv_meng
    else:
        qv_proces = qv_prev if rho_prev is None else (qv_prev * rho_prev) / rho

    T_nb = np.interp(H, df_enthalpy['H_range'], df_enthalpy['T_100']) #calculate nattebol temperatuur
    calculated_values = [x, pws, H, V, rho, pv, Td, formatted_pBar, T_nb,
                         Tdb_var,RH_var, qv_proces,Tdb_100,x_100] # hier niet afronden!! round() anders ga je verder rekenen met afgeronde getallen.

    return calculated_values

def calculate_saturated_vapor_pressure(Tdb, C):
    T = Tdb + 273.15
    if T <= 0:
        return 0.0
    if Tdb < 0:
        exponent = (
            C[1]/T + C[2] + C[3]*T + C[4]*T**2 +
            C[5]*T**3 + C[6]*T**4 + C[7]*safe_log(T)
        )
    else:
        exponent = (
            C[8]/T + C[9] + C[10]*T + C[11]*T**2 +
            C[12]*T**3 + C[13]*safe_log(T)
        )

    return safe_exp(exponent)
def calculate_partial_vapor_pressure(x, pressure):
    # Inputs: x in g/kg; Output: partial in Pa
    x = x / 1000  # convert to kg/kg
    return (x * pressure) / (0.62198  + x)
def calculate_humidity_ratio(pv, pressure):
    # Inputs: pv in Pa  Output: x in g/kg
    x = (0.62198 * pv) / (pressure - pv)
    return x * 1000  # Convert to g/kg
def calculate_enthalpy(Tdb, x):
    x = x / 1000  # x in g/kg to kg/kg
    return (1.006 * Tdb) + (x * (2501 + 1.86 * Tdb))
def calculate_humidity_ratio_from_enthalpy(h, Tdb):
    x = (h - 1.006 * Tdb) / (2501 + 1.86 * Tdb) #at pressure 101325 Pa
    return x * 1000  # Convert to g/kg
def calculate_relative_humidity(pv, pws):
    return max(0, min((pv / pws) * 100, 100))
def calculate_specific_volume(Tdb, x, pBar):
    return 0.2871 * (Tdb + 273.15) * (1 + 1.6078 * x / 1000) / (pBar / 1000)
def calculate_dew_point(pv, Tdb, C):
    if not pv or pv <= 0:
        return float('-inf')  # or return 0.0 or raise a ValueError

    pv_kPa = pv / 1000.0
    log_pv = safe_log(pv_kPa)
    log_pv2 = log_pv ** 2

    if Tdb < 0:
        return 6.09 + 12.608 * log_pv + 0.4959 * log_pv2
    else:
        log_pv3 = log_pv * log_pv2
        return (
            C[14]
            + C[15] * log_pv
            + C[16] * log_pv2
            + C[17] * log_pv3
            + C[18] * (pv_kPa ** 0.1984)
        )
def calculate_Tdb_from_enthalpy(h, x):
    """Calculate Tdb given enthalpy and humidity ratio (x in g/kg)."""
    x = x / 1000  #(x in kg/kg).
    return (h - 2501 * x) / (1.006 + 1.86 * x)
def infer_Tdb_RH_from_any_two(var1, val1, var2, val2, pressure=101325, C_values=None, lines_RH={}):
   # Validate that neither input is None
    if var1 is None or var2 is None:
        raise ValueError(f"Both variables must be provided. Got: var1={var1}, var2={var2}")
    if val1 is None or val2 is None:
        raise ValueError(f"Both values must be provided. Got: val1={val1}, val2={val2}")
    # Normalize variable names to expected keys
    keys = sorted([var1, var2])
    var_pair = "_".join(keys)
    val_dict = {var1: val1, var2: val2}
    # Validate keys presence
    for key in keys:
        if key not in val_dict:
            raise ValueError(f"Missing value for variable {key}")
    # Check if the variable pair combination is RH & Drogeboltemperatuur (Tdb) 1/9
    if var_pair == "RH_Tdb":
        return val_dict["Tdb"], val_dict["RH"]
    # option 2
    elif var_pair == "Tdb_Twb":
        Tdb = val_dict["Tdb"]
        Twb = val_dict["Twb"]

        # Step 1: Get x at Twb using 100% RH line
        x_values = lines_RH['x_values']
        y_values = lines_RH['onehondered_percent']
        closest_index = min(range(len(x_values)), key=lambda i: abs(x_values[i] - Twb))
        x_wb = y_values[closest_index]  # g/kg

        # Step 2: Get enthalpy at (Twb, x_wb)
        h_wb = calculate_enthalpy(Twb, x_wb)

        # Step 3: Minimize error between h(Tdb, x_guess) and h_wb
        def rh_error(RH_guess):
            RH_frac = RH_guess / 100
            pws = calculate_saturated_vapor_pressure(Tdb, C_values)
            pv = RH_frac * pws
            x_guess = calculate_humidity_ratio(pv, pressure)
            h_guess = calculate_enthalpy(Tdb, x_guess)
            return abs(h_guess - h_wb)

        result = minimize_scalar(rh_error, bounds=(1, 100), method='bounded')
        rh = round(result.x, 2) if result.success else 50.0  # fallback RH

        # pws_Tdb = calculate_saturated_vapor_pressure(Tdb, C_values)
        # pws_Twb = calculate_saturated_vapor_pressure(Twb, C_values)
        # pv = pws_Twb - ( 0.00066 * (1 + 0.00115 * Twb)) * pressure * (Tdb - Twb)
        # rh = calculate_relative_humidity(pv, pws_Tdb)  # Calculate relative humidity
        return Tdb, rh
    # option 3
    elif var_pair == "AH_Tdb":  
        x = val_dict["AH"]
        Tdb = val_dict["Tdb"]
        pws = calculate_saturated_vapor_pressure(Tdb, C_values)
        pv = calculate_partial_vapor_pressure(x, pressure) #(x * atm_pres) / (0.62198 * 1000 + x)  # in actual vapor pressure in Pa
        rh = calculate_relative_humidity(pv, pws)
        return Tdb, rh
        #option 4
    elif var_pair == "Tdb_h":
        Tdb = val_dict["Tdb"]
        h = val_dict["h"]
        pws = calculate_saturated_vapor_pressure(Tdb, C_values)
        x = ((h - 1.006 * Tdb) / (2501 + 1.86 * Tdb))*1000
        pv = calculate_partial_vapor_pressure(x, pressure)
        rh = calculate_relative_humidity(pv, pws)
        return Tdb, rh    
    #option 5
    elif var_pair == "AH_h":
        x = val_dict["AH"]
        h = val_dict["h"]

        def error(Tdb_guess):
            if Tdb_guess < -30 or Tdb_guess > 80:
                return 1e6
            h_guess = calculate_enthalpy(Tdb_guess, x)
            return abs(h_guess - h)

        result = minimize_scalar(error, bounds=(-30, 80), method='bounded')
        Tdb = result.x if result.success else 20  # fallback Tdb
         # Recalculate enthalpy at found Tdb and compare with input h
        h_check = calculate_enthalpy(Tdb, x)
        diff = abs(h_check - h)

        # Threshold: if the calculated enthalpy is too far off, it's likely invalid
        if diff > 1:  # You can tweak this threshold
            return 20.0, 50.0, True  # fallback Tdb, RH, invalid flag
        #Tdb = calculate_Tdb_from_enthalpy(h, x)  # in °C
        pv = calculate_partial_vapor_pressure(x, pressure)  # actual vapor pressure in Pa
        pws = calculate_saturated_vapor_pressure(Tdb, C_values)  # in Pa
        rh = calculate_relative_humidity(pv, pws)


        return Tdb, rh
    # option 6
    elif var_pair == "AH_Twb":
        x = val_dict["AH"] 
        Twb = val_dict["Twb"]
        #Solving enthalpy(Tdb, x) == enthalpy(Twb, x_wb)
        x_values = lines_RH['x_values']
        y_values = lines_RH['onehondered_percent']
        closest_index = min(range(len(x_values)), key=lambda i: abs(x_values[i] - Twb))
        x_wb = y_values[closest_index]
    
        h_wb = calculate_enthalpy(Twb, x_wb)
        # Step 3: Minimize error between h(Tdb, x) and h_wb
        def error(Tdb_guess):
            if Tdb_guess < Twb:  # Physically invalid
                return 1e6
            h_guess = calculate_enthalpy(Tdb_guess, x)
            return abs(h_guess - h_wb)
        result = minimize_scalar(error, bounds=(Twb, 60), method='bounded')
        Tdb = result.x if result.success else 20  # fallback Tdb
        pv = calculate_partial_vapor_pressure(x, pressure)  # actual vapor pressure in Pa
        pws = calculate_saturated_vapor_pressure(Tdb, C_values)  # saturation pressure at Twb
        rh = calculate_relative_humidity(pv, pws)
        return Tdb, rh
    # option 7
    elif var_pair == "RH_h":
        rh = val_dict["RH"]  # in %
        h = val_dict["h"]    # in kJ/kg
        RH_frac = rh / 100   # Convert to 0–1

        def error(Tdb_guess):
            pws = calculate_saturated_vapor_pressure(Tdb_guess, C_values)
            pv = RH_frac * pws
            x = calculate_humidity_ratio(pv,pressure)
            h_guess = calculate_enthalpy(Tdb_guess, x)
            return abs(h_guess - h)

        result = minimize_scalar(error, bounds=(0, 60), method='bounded')
        Tdb = result.x if result.success else None

        return Tdb, rh
    # option 8
    elif var_pair == 'RH_Twb':
        rh = val_dict["RH"]
        Twb = val_dict["Twb"]
        #get the x-value of the wetbulb temperature
        x_values = lines_RH['x_values']
        y_values = lines_RH['onehondered_percent']
        closest_index = min(range(len(x_values)), key=lambda i: abs(x_values[i] - Twb))
        x = y_values[closest_index] 
        h = calculate_enthalpy(Twb, x)
        
        RH_frac = rh/ 100  # Convert % to 0–1

        def error(Tdb_guess):
            pws = calculate_saturated_vapor_pressure(Tdb_guess, C_values)
            pv = RH_frac * pws
            x = calculate_humidity_ratio(pv,pressure)
            h_guess = calculate_enthalpy(Tdb_guess, x)
            return abs(h_guess - h)

        result = minimize_scalar(error, bounds=(0, 60), method='bounded')
        Tdb = result.x if result.success else None
        return Tdb, rh
    

    else:
        raise ValueError(f"Unsupported variable pair: {var_pair}")
    
def infer_Tdb_RH_from_proces(calc_prev_values,proces,function1,function2,Input1,Input2,Input3,Input4,Input5,
                                                      Input6, Input7,Input8,Input9, pressure, C_values,lines_RH):
    if proces == 'heat' and function1 == 'power':
        return heat_power(calc_prev_values[2],calc_prev_values[11],Input2,calc_prev_values[0],calc_prev_values[4],pressure, C_values)
    if proces == 'heat' and function1 == 'deltaT':
        return heat_DeltaT(calc_prev_values[9],Input2,calc_prev_values[5], C_values)
    if proces == 'heat' and function1 == 'deltaH':
        return heat_DeltaH(calc_prev_values[2],Input2,calc_prev_values[0],pressure,C_values)
    if proces == 'heat' and function1 == 'toTemp':
        return heat_ToT(Input2,calc_prev_values[5],C_values)
    if proces == 'cool' and function1 == 'power':
        return cool_power(calc_prev_values[2], Input1, Input2,calc_prev_values[9],calc_prev_values[0],calc_prev_values[11],calc_prev_values[4],calc_prev_values[6],pressure, C_values,lines_RH)
    if proces == 'cool' and function1 == 'deltaT':
        return cool_DeltaT(Input1, Input2,calc_prev_values[6],calc_prev_values[0],calc_prev_values[9],pressure,C_values,lines_RH)
    if proces == 'cool' and function1 == 'deltaH':
        return cool_DeltaH(calc_prev_values[2], Input1,Input2,calc_prev_values[9],calc_prev_values[0],calc_prev_values[11],calc_prev_values[4],calc_prev_values[6],pressure, C_values,lines_RH)
    if proces == 'cool' and function1 == 'toTemp':
        return cool_ToT(Input1, Input2,calc_prev_values[6],calc_prev_values[0],calc_prev_values[9],pressure,C_values,lines_RH)
    if proces == 'humid' and function2 == 'AdiabaticX':
        return humid_adiabaticX(Input2,calc_prev_values[2],calc_prev_values[0],calc_prev_values[8], C_values, pressure)
    if proces == 'humid' and function2 == 'AdiabaticRH':
        return humid_adiabaticRV(Input2,calc_prev_values[2],calc_prev_values[10], C_values, pressure)
    if proces == 'humid' and function2 == 'IsoX':
        return humid_isoX(Input2,calc_prev_values[9],calc_prev_values[0],C_values,pressure)
    if proces == 'humid' and function2 == 'IsoRH':
        return humid_isoRV(Input2,calc_prev_values[9],calc_prev_values[10])
    if proces == 'mix':
        return mix(Input3,Input4,Input5,Input6,calc_prev_values[9],calc_prev_values[0], calc_prev_values[11],C_values,pressure)
    if proces == 'heat_rec':
        return heat_rec(Input6,Input7,Input8,Input4,calc_prev_values[9],calc_prev_values[0],C_values,pressure)
    if proces == 'cust_point':
        return cust_point(Input9,Input6)
    else:
        return 0,0

def heat_power(h1, qv_prev, Q, x, rho_prev, pressure=101325, C_values=None):
    """Calculate the Tdb and RH based on heating process with given power input."""
    qm = qv_prev * rho_prev / 3600  # m³/h to kg/s
    h2 = h1 + (Q / qm)    # new enthalpy in kJ/kg
    
    Tdb = calculate_Tdb_from_enthalpy(h2, x)
   
    pv = calculate_partial_vapor_pressure(x, pressure)
    pws = calculate_saturated_vapor_pressure(Tdb, C_values)
    rh = calculate_relative_humidity(pv, pws)

    return Tdb, rh
def heat_DeltaT(T1, DeltaT, pv, C_values=None):
    """ Calculate the Tdb and RH based on heating proces and given Power"""
    Tdb = T1 + DeltaT # Calculate the temperature
    pws = calculate_saturated_vapor_pressure(Tdb, C_values)
    rh = calculate_relative_humidity(pv, pws)
    return Tdb, rh
def heat_DeltaH(h1, DeltaH, x, pressure=101325,C_values=None):
    h2 = h1 +  DeltaH # Calculate the enthalpy at the end of the process
    Tdb = calculate_Tdb_from_enthalpy(h2, x)
    pv = calculate_partial_vapor_pressure(x, pressure)
    pws = calculate_saturated_vapor_pressure(Tdb, C_values)
    rh = calculate_relative_humidity(pv, pws)
    return Tdb, rh 
def heat_ToT(ToT ,pv,C_values=None):
    Tdb = ToT  # Calculate the temperature
    pws = calculate_saturated_vapor_pressure(Tdb, C_values)    # Saturated vapor pressure from the Magnus equation
    rh = calculate_relative_humidity(pv, pws)
    return Tdb, rh
def cool_power(h_prev, Ef, Q, Tdb_first, x_prev, qv_prev, rho_prev,Td_prev, pressure=101325,C_values=None, lines_RH=None):
    """ Calculate the Tdb and RH based on heating proces and given Power"""
    qm = qv_prev * rho_prev / 3600  # Convert volumetric flow (m3/h) to mass flow (kg/s)
    h_100 = h_prev - ((Q) / qm ) # Calculate the enthalpy at the end of the process
    hd_start  = calculate_enthalpy(Td_prev,x_prev) # #enthalpy at dewpoint of previous point
    Tdb_100 = None
    x_100 = None
    if h_100 > hd_start:
        Tdb = calculate_Tdb_from_enthalpy(h_100, x_prev) #this is Tdb without drying
        pv = calculate_partial_vapor_pressure(x_prev, pressure)
        pws = calculate_saturated_vapor_pressure(Tdb, C_values)
        rh = calculate_relative_humidity(pv, pws)
    elif h_100 < hd_start:
        Tdb_lines = lines_RH['x_values']
        x_values = lines_RH['onehondered_percent']
        h_values = [calculate_enthalpy(temp, hum_ratio) for temp, hum_ratio in zip(Tdb_lines, x_values)]
        Tdb_100, x_100 = interpolate_Tdb_and_x(h_100, Tdb_lines, x_values, h_values) #this is Tdb and x  at EF = 100% 

        x2 = x_prev - Ef/100*(x_prev-x_100)
        Tdb = Tdb_first - Ef/100*(Tdb_first - Tdb_100) #this is Tdb at EF (%)
        
        pv2 = calculate_partial_vapor_pressure(x2, pressure)
        pws2 = calculate_saturated_vapor_pressure(Tdb, C_values)
        rh = calculate_relative_humidity(pv2, pws2) 
    
    return Tdb, rh, Tdb_100,x_100   
def cool_DeltaT(Ef, DeltaT, Td_prev, x_prev ,Tdb_prev,pressure,C_value, lines_RH={}):
    ToT = Tdb_prev-DeltaT
    Tdb, rh,Tdb_100, x_100 = cool_ToT(Ef, ToT, Td_prev, x_prev ,Tdb_prev,pressure,C_value, lines_RH)
    return Tdb, rh,Tdb_100, x_100
def cool_DeltaH(h_prev, Ef, DeltaH, Tdb_first, x_prev, qv_prev, rho_prev,Td_prev, pressure,C_values, lines_RH):
    qm = qv_prev * rho_prev / 3600
    Q = qm * (DeltaH)
    Tdb, rh ,Tdb_100, x_100 = cool_power(h_prev, qv_prev, Ef, Q, Tdb_first, x_prev, rho_prev,Td_prev, pressure,C_values, lines_RH)
    return Tdb, rh ,Tdb_100, x_100
def cool_ToT(Ef, ToT, Td_prev, x_prev ,Tdb_prev,pressure=101325,C_values=None, lines_RH=None):
    Tdb_100 = None
    x_100 = None
    if ToT > Td_prev: 
        Tdb = ToT # Calculate the temperature
        pws = calculate_saturated_vapor_pressure(Tdb, C_values)   
        pv_prev = calculate_partial_vapor_pressure(x_prev, pressure) # Saturated vapor pressure from the Magnus equation
        rh = calculate_relative_humidity(pv_prev, pws)
    elif ToT <= Td_prev:#als ToTemp onder dauwpunt komt te liggen wordt er ontvochtigd. 
        Tdb_100 = ToT   
        #get the x-value of the T_100 temperature
        x_values = lines_RH['x_values']
        y_values = lines_RH['onehondered_percent']
        closest_index = min(range(len(x_values)), key=lambda i: abs(x_values[i] - Tdb_100))
        x_100 = y_values[closest_index] # x-value at 100% RV
        x2 = x_prev - Ef/100*(abs(x_prev-x_100)) #x-value at efficiency
        Tdb = Tdb_prev- Ef/100*(abs(Tdb_prev-ToT))
        pws = calculate_saturated_vapor_pressure(Tdb, C_values) 
        pv = calculate_partial_vapor_pressure(x2, pressure)
        rh = calculate_relative_humidity(pv, pws) 
    return Tdb, rh, Tdb_100, x_100
def humid_adiabaticX(DeltaX, h_prev,x_prev, Tnb_prev ,C_values=None, pressure=101325):

    """ Calculate the Tdb and RH based on adiabatic humidification process and given DeltaX"""
    x2 = x_prev + DeltaX  # Calculate the new humidity ratio
    x_100 = calculate_humidity_ratio_from_enthalpy(h_prev, Tnb_prev)  # Calculate the humidity ratio at 100% RH
    x2 = min(x_100, x2)  # Limit to 100% RH
    Tdb = calculate_Tdb_from_enthalpy(h_prev, x2)
    pws = calculate_saturated_vapor_pressure(Tdb, C_values)
    pv = calculate_partial_vapor_pressure(x2, pressure)  # Calculate the partial pressure of water vapor
    rh = calculate_relative_humidity(pv, pws)
    return Tdb, rh 
def humid_adiabaticRV(DeltaRV, h_start, RV_start, C_values=None,pressure=101325):
    RV_end = RV_start + DeltaRV  # Calculate the new relative humidity
    RV_end = min(RV_end, 100)  # Ensure RV does not exceed 100%
    RV_frac = RV_end / 100   # Convert to 0–1
    def error(Tdb_guess):
        # Step 1: Get saturation vapor pressure at Tdb
        pws = calculate_saturated_vapor_pressure(Tdb_guess, C_values)
        pv = RV_frac * pws
        x = calculate_humidity_ratio(pv,pressure)
        h_guess =calculate_enthalpy (Tdb_guess, x) #1.006 * Tdb_guess + W * (2501 + 1.86 * Tdb_guess)
        return abs(h_guess - h_start)

    result = minimize_scalar(error, bounds=(0, 60), method='bounded')
    Tdb = result.x if result.success else None
    return Tdb, RV_end
def humid_isoX(DeltaX, T_start, x_start, C_values=None,pressure=101325):
    Tdb = T_start
    x2= x_start + DeltaX  # Calculate the new humidity ratio
    pv = calculate_partial_vapor_pressure(x2,pressure)  # Calculate the partial pressure of water vapor
    pws = calculate_saturated_vapor_pressure(Tdb, C_values)  # Satur
    rh = calculate_relative_humidity(pv, pws)
    return Tdb, rh
def humid_isoRV(DeltaRV, T_start, RV_start):
    Tdb = T_start
    rh= RV_start + DeltaRV  # Calculate the new humidity ratio
    rh = min(rh, 100)  # Ensure RV does not exceed 100%
    return Tdb, rh
def mix(eta_air,T_extra,qv_extra,RV_extra,T_start, x_start, qv_start, C_values=None,pressure=101325):
    qv_meng = qv_extra + qv_start*eta_air/100
    Tdb = (T_start*qv_start*eta_air/100+T_extra*qv_extra)/qv_meng
    pws = calculate_saturated_vapor_pressure(T_extra, C_values)
    
    pv = pws * RV_extra/100
    x_extra = calculate_humidity_ratio(pv, pressure) 
    x2 = (x_start*qv_start*eta_air/100+x_extra*qv_extra)/qv_meng
    pws2 = calculate_saturated_vapor_pressure(Tdb, C_values)
    pv2 = calculate_partial_vapor_pressure(x2,pressure) #(x2/1000*pressure)/ (0.62198 + x2/1000) #check on all if not devided by 1000
    rh = calculate_relative_humidity(pv2, pws2)
 
    return Tdb, rh, T_extra,x_extra,qv_meng
def heat_rec(RV_out,eta_x,eta_th,Tdb_out,Tdb_start,x_start,C_values,pressure):
    
    pws = calculate_saturated_vapor_pressure(Tdb_out,C_values)
    pv = pws* RV_out/100
    x_out = calculate_humidity_ratio(pv,pressure)#(0.62198 * pv) *1000 / (pressure - pv)
    T_rec= Tdb_start-eta_th/100*(Tdb_start-Tdb_out)
    x_rec = x_start -eta_x/100*(x_start-x_out)
    pv_rec = calculate_partial_vapor_pressure(x_rec,pressure)#(x_rec/1000*pressure)/ (0.62198 + x_rec/1000)
    pws_rec= calculate_saturated_vapor_pressure(T_rec, C_values)
    rh_rec = calculate_relative_humidity(pv_rec, pws_rec)

    return T_rec, rh_rec, Tdb_out, x_out
def cust_point(Tdb_cust,RH_cust):
    return Tdb_cust,RH_cust

def calculate_proces_values(prev, current):
    TOLERANCE = 0.01  # g/kg precision for Delta x

    delta_Tdb = abs(current[9] - prev[9]) # Tdb
    delta_H = abs(current[2] - prev[2]) # Enthalpy
    delta_x = abs(current[0] - prev[0]) # x
    c_air = 1.006  # Specific heat capacity of air in kJ/kg·K
    qm = (prev[4] * prev[11]) / 3600  # Mass flow rate in kg/s
    P_total = abs((current[2] - prev[2])) * qm

    # Check for meaningful humidity difference
    if delta_x > TOLERANCE:
        r_l = ((current[2] - prev[2]) - (current[9] - prev[9])) / ((current[0] - prev[0]) / 1000)
        P_latent = r_l * qm * abs((current[0] - prev[0]) / 1000)
        P_voelbaar = qm * c_air * abs((current[9] - prev[9]))
    else:
        P_latent = 0
        P_voelbaar = P_total
    # Calculate VWF (Voelbare Warmte Fractie) tussen 0 en de 1 altijd
    if abs(P_total) < TOLERANCE:
        VWF = 0
    else:
        VWF = P_voelbaar / P_total
        if not (0 <= VWF <= 1):
            VWF = 0

    proces_values = [delta_Tdb, delta_x, delta_H, P_total, P_voelbaar, P_latent, VWF]
    return proces_values

def interpolate_Tdb_and_x(h_100, Tdb_lines, x_values, h_values):
    for i in range(len(h_values) - 1):
        h1, h2 = h_values[i], h_values[i + 1]
        if h1 <= h_100 <= h2:
            # Linear interpolation weight
            ratio = (h_100 - h1) / (h2 - h1)
            
            Tdb_interp = Tdb_lines[i] + ratio * (Tdb_lines[i + 1] - Tdb_lines[i])
            x_interp = x_values[i] + ratio * (x_values[i + 1] - x_values[i])
            
            return Tdb_interp, x_interp

    raise ValueError("h_100 is out of bounds of the h_values range.")

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default 
def safe_sqrt(x, default=0.0):
    try:
        return math.sqrt(x) if x >= 0 else default
    except (ValueError, TypeError):
        return default
def safe_log(x, default=0.0):
    try:
        return math.log(x) if x > 0 else default
    except (ValueError, TypeError):
        return default
def safe_acos(x, default=0.0):
    try:
        if -1 <= x <= 1:
            return math.acos(x)
        return default
    except (ValueError, TypeError):
        return default
def safe_exp(x, default=float('inf'), max_input=700):
    try:
        x = float(x)
        if x > max_input:
            return default  # Prevent OverflowError
        return math.exp(x)
    except (ValueError, TypeError, OverflowError):
        return default


def generate_pdf_file(request):
    if request.method != "POST" or 'SavePDFButton' not in request.POST:
        return HttpResponse("Invalid request", status=400)

    # --- gather inputs ---
    pts       = json.loads(request.POST.get("table_points_json",   "[]"))
    procs     = json.loads(request.POST.get("table_process_json", "[]"))
    chart_b64 = request.POST.get("chart_image_base64")
    title     = request.POST.get("project_title",      "Mollierdiagram")
    user      = request.POST.get("username",           "Gebruiker onbekend")
    stamp     = datetime.now().strftime('%d %B %Y %H:%M')

    # --- setup canvas ---
    buffer = BytesIO()
    c      = canvas.Canvas(buffer, pagesize=A4)
    w, h   = A4

    # --- PAGE 1 ---

    # Title (moved down 35pt)
    c.setFont('Helvetica', 18)
    c.drawCentredString(w/2, h-35, title)

    # Chart
    if chart_b64:
        img_data = base64.b64decode(chart_b64)
        img      = ImageReader(BytesIO(img_data))
        img_h    = h /2 
        c.drawImage(img, 20, h - 50 -img_h, width=w-40, height=img_h, preserveAspectRatio=True)

    # Table styles
    styles       = getSampleStyleSheet()
    normal       = styles["Normal"]
    header_style = ParagraphStyle(
        'table_header',
        parent=normal,
        fontName='Helvetica-Bold',
        textColor=colors.white,
        alignment=1,
        leading=normal.leading,
    )
    unit_style   = ParagraphStyle(
        'units',
        parent=normal,
        fontSize=8,
        textColor=colors.grey,
        leading=10,
        alignment=1,
    )
    data_style   = ParagraphStyle('data', parent=normal,
                                  fontSize=9, alignment=1)
    def fmt(v):
        s = str(v)
        # if it's a float-like or contains a '.', replace with comma
        if any(c.isdigit() for c in s) and '.' in s:
            s = s.replace('.', ',')
        return s

    def draw_table(data, headers, col_widths, y_top):
        if not data:
            return
        # header row
        data[0] = [Paragraph(cell, header_style) for cell in headers]
        # unit row
        if len(data) > 1:
            data[1] = [Paragraph(str(v), unit_style) for v in data[1]]
        # all subsequent rows: wrap & format numbers
        for i in range(2, len(data)):
            data[i] = [Paragraph(fmt(v), data_style) for v in data[i]]
        # row heights
        row_heights = [22, 15] + [None] * (len(data) - 2)
        tbl = Table(data, colWidths=col_widths, rowHeights=row_heights)
        tbl.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0), colors.HexColor('#3DAB39')),
            ('TEXTCOLOR', (0,0),(-1,0), colors.white),
            ('VALIGN',    (0,0),(-1,0), 'MIDDLE'),
            ('ALIGN',     (0,1),(-1,1), 'CENTER'),   # <-- center units row
            ('VALIGN',    (0,1),(-1,1), 'MIDDLE'),
            ('GRID',      (0,0),(-1,-1), 0.5, colors.white),
            ('FONTNAME',  (0,0),(-1,-1), 'Helvetica'),
            ('FONTSIZE',  (0,1),(-1,1), 8),
            ('TEXTCOLOR', (0,1),(-1,1), colors.grey),
            ('FONTSIZE',  (0,2),(-1,-1), 9),
            ('ALIGN',     (0,2),(-1,-1), 'CENTER'),
        ]))
        tbl.wrapOn(c, w, h)
        tbl.drawOn(c, 20, y_top - 18 * len(data))

    # columns

    total_w = w - 40
    fracs   = [0.14,0.15,0.15,0.08,0.07,0.07,0.08,0.10,0.08,0.08]
    col_w   = [total_w * p for p in fracs]
    point_hdrs = ["Punt","T<sub>db</sub>","T<sub>nb</sub>","T<sub>dauw</sub>",
                  "X","H","RH","P<sub>w</sub>","ρ","Q<sub>v</sub>"]
    proc_hdrs  = ["Proces","Actie 1","Actie 2","ΔT<sub>db</sub>","ΔX","ΔH",
                  "P<sub>totaal</sub>","P<sub>voelbaar</sub>","P<sub>latent</sub>","VWF"]
    #draw point table with title
    point_table_y = h - 500
    c.setFont('Helvetica', 14)
    c.drawString(20, point_table_y+10, "Punten in het Mollierdiagram")
    draw_table(pts,   point_hdrs, col_w, point_table_y)
    #draw proeces table with title
    c.setFont('Helvetica', 14)
    proc_table_y = h -650
    c.drawString(20, proc_table_y+10, "Processen in het Mollierdiagram")
    draw_table(procs, proc_hdrs,  col_w, proc_table_y)

    # Footer
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawRightString(w-20, 20, "Pagina 1/2")
    c.drawString(20, 20, stamp)
    c.drawString(w/2, 20, f"Gebruiker: {user}")

    c.showPage()

    # --- PAGE 2 ---

    # --- PAGE 2: info table with transparent lines ---

    # styles for page 2
    key_style  = ParagraphStyle('key',  parent=normal,
                                fontName='Helvetica-Bold', fontSize=11, leading=14,leftIndent=28)
    desc_style = ParagraphStyle('desc', parent=normal,
                                fontName='Helvetica',      fontSize=11, leading=14)

    params = [
        ("T<sub>db</sub>:",   "Drogeboltemperatuur"),
        ("T<sub>nb</sub>:",   "Natteboltemperatuur"),
        ("T<sub>dauw</sub>:", "Dauwpuntstemperatuur"),
        ("X:",                "Vochtgehalte"),
        ("H:",                "Entalpie"),
        ("RH:",               "Relatieve luchtvochtigheid"),
        ("P<sub>w</sub>:",    "Partiële Dampdruk"),
        ("ρ:",                "Luchtdichtheid"),
        ("Q<sub>v</sub>:",    "Luchtdebiet"),
        ("P<sub>totaal</sub>:","Voelbare + latente vermogen"),
        ("P<sub>voelbaar</sub>:","Voelbare vermogen"),
        ("P<sub>latent</sub>:","Latente vermogen"),
        ("VWF:",              "Voelbare Warmte Factor"),
    ]

    # build table data using Paragraphs
    data = [
        [Paragraph(key,  key_style),
         Paragraph(desc, desc_style)]
        for key, desc in params
    ]

    # two columns: first col 100pt, second col fills remaining width
    info_table = Table(data, colWidths=[100, (w-40)-100], hAlign='LEFT')
    info_table.setStyle(TableStyle([
        # no grid lines at all:
        ('GRID',       (0,0), (-1,-1), 0, colors.transparent),
        ('VALIGN',     (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING',(0,0), (-1,-1), 0),
        ('RIGHTPADDING',(0,0),(-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING',(0,0),(-1,-1),2),
    ]))

    # draw a header
    c.setFont('Helvetica-Bold',14)
    c.drawString(40, h-60, "Informatie over de Processen")

    # place table in a frame
    frame = Frame(20, 60, w-40, h-140, showBoundary=0)
    frame.addFromList([info_table], c)

    # warning in red below the table
    warning_style = ParagraphStyle('warn', parent=normal,
                                   fontName='Helvetica-Bold', fontSize=9,
                                   textColor=colors.red, leading=14,
                                   leftIndent=20)
    warning_title = Paragraph("Waarschuwing:", warning_style)
    warning_text  = Paragraph(
        "De berekende en gevisualiseerde resultaten kunnen afwijken van de ingevoerde waarden "
        "door onnauwkeurigheden, fysieke beperkingen of grafiekbeperkingen. De trajecten van de "
        "luchtprocessen worden als rechte lijnen naar de resulterende waarde weergegeven, maar "
        "kunnen in werkelijkheid gekromd zijn door condensatie.",
        warning_style
    )

    # draw warning directly
    warning_title.wrapOn(c, w-40, 50)
    warning_title.drawOn(c, 20, 80)
    warning_text.wrapOn(c, w-40, 60)
    warning_text.drawOn(c, 20, 40)

     # Footer
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawRightString(w-20, 20, "Pagina 2/2")
    c.drawString(20, 20, stamp)
    c.drawString(w/2, 20, f"Gebruiker: {user}")
    
    c.save()
    buffer.seek(0)
    resp = HttpResponse(buffer, content_type='application/pdf')
    resp['Content-Disposition'] = 'attachment; filename="mollierdiagram.pdf"'
    return resp
