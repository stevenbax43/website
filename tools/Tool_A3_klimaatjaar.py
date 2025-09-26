import pandas as pd 
import numpy as np
from datetime import datetime
import math, json, base64
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle, Paragraph, Frame, Spacer

def klimaatjaar(request):
    
    OnOffHours, HeatCoolEnergy, line_chart_data, line_chart_data_hoursONOFF, cumulative_data,limit_values, energy_values = [], [], {}, {},{}, [], []
    designTempheat, maxTempHeat,HeatBuildingMax, HeatBuildingMin,designTempcool, maxTempCool, CoolBuildingMax,CoolBuildingMin= 0,0,0,0,0,0,0,0

    if request.method =='POST':
        startdag, einddag = map(int, [request.POST.get('startdag'), request.POST.get('einddag')])
        startuur, einduur = map(int,[request.POST.get('startuur'), request.POST.get('einduur')])
        startTemp, eindTemp = map(int,[request.POST.get('starttemp'), request.POST.get('eindtemp')])
        method = request.POST.get('method')
  
        OnOffHours, df_Temp, df= OnOffTime(startdag,einddag,startuur,einduur, method, startTemp, eindTemp)
        
        #all buildings inputs 
        designTempheat, maxTempHeat, HeatBuildingMax, HeatBuildingMin = map(int, [
            request.POST.get('designTempheat'), request.POST.get('maxTempHeat'), request.POST.get('HeatBuildingMax'), request.POST.get('HeatBuildingMin')])
        designTempcool, maxTempCool, CoolBuildingMax, CoolBuildingMin = map(int, [
            request.POST.get('designTempcool'), request.POST.get('maxTempCool'), request.POST.get('CoolBuildingMax'), request.POST.get('CoolBuildingMin')])
        HeatCoolEnergy, df_Temp = PowerEnergy(df_Temp, designTempheat, maxTempHeat, HeatBuildingMax,HeatBuildingMin, designTempcool, maxTempCool, CoolBuildingMax, CoolBuildingMin)
        

        #cumulative belastingduurkromme maken. 
        Limit_Heat_max, Limit_Heat_min, Limit_Cool_Max, Limit_Cool_Min = map(int, [
            request.POST.get('LimitHeatMax'), request.POST.get('LimitHeatMin'), request.POST.get('LimitCoolMax'),request.POST.get('LimitCoolMin') ])
             
        df_cum, limit_values, energy_values = cumulative_graph(df_Temp, Limit_Heat_max,Limit_Heat_min,Limit_Cool_Max,Limit_Cool_Min, HeatBuildingMin,CoolBuildingMax, HeatBuildingMax, CoolBuildingMin)

        # prepare df_Temp for download_excel 
        df_Temp_json = df_Temp.to_dict(orient='records')
        request.session['df_Temp'] = df_Temp_json
        # prepare df_inputs for download_excel
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        input_data = {
            'Aangemaakt op': [current_time],
            'Aangemaakt door':[current_time],
            'startdag': [startdag],
            'einddag': [einddag],
            'startuur': [startuur],
            'einduur': [einduur],
            'OntwerpTempHeat': [designTempheat],
            'maxTempHeat': [maxTempHeat],
            'HeatPowerMax': [HeatBuildingMax],
            'OntwerpTempCool': [designTempcool],
            'maxTempCool': [maxTempCool],
            'CoolPowerMax': [CoolBuildingMax]
        }

        df_Inputs = pd.DataFrame(input_data)
        df_Inputs_json = df_Inputs.to_dict(orient='records')
        request.session['df_Inputs'] = df_Inputs_json

        #create list for chartdata in HTML 
        line_chart_data = {
        'x_values': df_Temp['TempRange'].tolist(),  # X-axis values from 0 to 40
        'heating_curve': df_Temp['HeatPower'].tolist(),  # Dataset 1 y-axis values
        'cooling_curve': df_Temp['CoolPower'].tolist(),   # Dataset 2 y-axis values
        }
        line_chart_data_hoursONOFF = {
        'x_values2': df_Temp['TempRange'].tolist(),  # X-axis values from 0 to 40
        'OnHours': df_Temp['sumOnTemp'].tolist(),  # Dataset 1 y-axis values
        'OffHours': df_Temp['sumOffTemp'].tolist(),
        'CumOnHours': df_Temp['CumOnHours'].tolist(),  
        'CumOnHoursBtwTemp': df_Temp['CumOnHoursBtwTemp'].tolist(), # Dataset 2 y-axis values   # Dataset 2 y-axis values
        }
        cumulative_data = {
        'x_values3': df_cum['sumOnCum'].tolist(),  # X-axis values from 0 to 40
        'Q_heat': df_cum['HeatPower'].tolist(),  # Dataset 1 y-axis values
        'Q_cool': df_cum['CoolPower'].tolist(),   # Dataset 2 y-axis values
        }
        
        # prepare df for download_excel 
        df['YYYYMMDD'] = df['YYYYMMDD'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
        df_json = df.to_dict(orient='records')
        request.session['df'] = df_json
    return  [OnOffHours,HeatCoolEnergy,line_chart_data,line_chart_data_hoursONOFF, cumulative_data,limit_values, energy_values]

def OnOffTime(startday,endday,starthour,endhour, method, startTemp, eindTemp):
    df = pd.DataFrame()
    if int(method) == 1:
        df = pd.read_csv('tools/static/tools/files/Klimaatjaar2023deBilt.csv', sep=';')
    elif int(method) == 2:
        df = pd.read_csv('tools/static/tools/files/Klimaatjaar2018deBilt.csv', sep=';')
    elif int(method) == 3:
        df = pd.read_csv('tools/static/tools/files/KlimaatjaarNEN5060Energie2018.csv', sep=';')
    else: 
        print('error loading page.')

    df['YYYYMMDD'] = pd.to_datetime(df['YYYYMMDD'], format='%Y%m%d')
    df['day_of_week'] = df['YYYYMMDD'].dt.dayofweek+1
    
    # werkdagen en daguren in range van input
    df['within_range_day'] = df['day_of_week'].apply(lambda x: 1 if startday <= x <= endday else 0)
    df['within_range_hour'] = df['HH'].apply(lambda x: 1 if starthour <= x <= endhour else 0)
    
    #bedrijfssituatie ON/OFF
    df['onTime'] = df['within_range_day'] * df['within_range_hour']
    df['onTemp'] = df.apply(lambda row: row['T']/10 if row['onTime'] == 1 else np.nan, axis=1)
    df['offTemp'] = df.apply(lambda row: row['T']/10 if row['onTime'] == 0 else np.nan, axis=1)

    #input temperatuur, create another dataframe 
    lowTemp = -20
    highTemp = 40
    df_Temp = pd.DataFrame({'TempRange': range(lowTemp, highTemp + 1 )})
    df_Temp['sumOnTemp'] = df_Temp['TempRange'].apply(lambda x: ((df['onTemp'] < x) & (df['onTemp'] >= x-1)).sum())
    df_Temp['sumOffTemp'] = df_Temp['TempRange'].apply(lambda x: ((df['offTemp'] < x) & (df['offTemp'] >= x-1)).sum())
    #bepaal cumulatieve waarden en maak gebruik van een range in vervolg waarden.
    df_Temp['CumOnHours'] = df_Temp['sumOnTemp'].cumsum()
    cum_up = df_Temp.loc[df_Temp['TempRange'] == eindTemp, 'CumOnHours'].values[0]
    cum_below = df_Temp.loc[df_Temp['TempRange'] == startTemp, 'CumOnHours'].values[0]   
    cum_between = cum_up - cum_below
    df_Temp['sumOnHoursTemp'] =df_Temp.apply(lambda row: row['sumOnTemp'] if startTemp <= row['TempRange'] <= eindTemp else 0, axis=1)
    df_Temp['CumOnHoursBtwTemp'] = df_Temp.apply(lambda row: row['CumOnHours'] if startTemp <= row['TempRange'] <= eindTemp else 0, axis=1)
    
    OnTimeHours = df_Temp['sumOnTemp'].sum()-cum_between
    OffTimeHours = df_Temp['sumOffTemp'].sum() +OnTimeHours
    OnOffHours = [cum_between, OffTimeHours]
     

    return OnOffHours, df_Temp, df

def PowerEnergy(df_Temp,designTempheat,maxTempHeat,HeatPowerMax,HeatPowerMin, designTempcool,maxTempCool,CoolPowerMax, CoolPowerMin):
    #Vermogen & Energie 
    #bereken stooklijn verwarmen

    slopeHeat = (HeatPowerMax-HeatPowerMin) / ((designTempheat)-maxTempHeat)
    interceptHeat = HeatPowerMax - slopeHeat * (designTempheat)
    df_Temp['HeatPower'] = np.where((df_Temp['TempRange'] >= designTempheat) & (df_Temp['TempRange'] <= maxTempHeat ),
                                    slopeHeat * df_Temp['TempRange'] + interceptHeat,
                                    np.where(df_Temp['TempRange'] < designTempheat, HeatPowerMax, HeatPowerMin)).round(2)
    df_Temp['Q_heat[MWh]'] = (df_Temp['HeatPower']/1000 * df_Temp['sumOnHoursTemp']).round(2)
    HeatEnergy = df_Temp['Q_heat[MWh]'].sum()

    #bereken stooklijn koelen

    slopeCool = (CoolPowerMax-CoolPowerMin) / ((maxTempCool)-designTempcool)
    interceptCool = CoolPowerMax - slopeCool * (maxTempCool)
    df_Temp['CoolPower'] = np.where((df_Temp['TempRange'] >= designTempcool) & (df_Temp['TempRange'] <= maxTempCool ),
                                    slopeCool * df_Temp['TempRange'] + interceptCool,
                                    np.where(df_Temp['TempRange'] < designTempcool, CoolPowerMin,CoolPowerMax)).round(1)

    df_Temp['Q_cool[MWh]'] = (df_Temp['CoolPower']/1000 * df_Temp['sumOnHoursTemp']).round(1)
    CoolEnergy = df_Temp['Q_cool[MWh]'].sum()
    HeatCoolEnergy = [round(HeatEnergy), round(CoolEnergy)]
    #print(df_Temp)
    #prepare line_chart_data


    return HeatCoolEnergy, df_Temp

def cumulative_graph(df_Temp, Limit_Heat_max,Limit_Heat_min,Limit_Cool_Max,Limit_Cool_Min, HeatBuildingMin,CoolBuildingMax, HeatBuildingMax, CoolBuildingMin):
    #bereken belastingduurkromme 
   
    df_cum = df_Temp 
    df_cum['sumOnCum'] = df_cum['sumOnHoursTemp'].cumsum()
    #verwarmen piek, midden en basislast
    df_cum['Q_heat_piek'] = df_cum.apply(lambda row: ((row['HeatPower'] - Limit_Heat_max) / 1000 * row['sumOnHoursTemp']) if row['HeatPower'] > Limit_Heat_max else 0, axis=1)
    df_cum['Q_heat_btwn'] = df_cum.apply(lambda row: ((row['HeatPower'] - Limit_Heat_min) / 1000 * row['sumOnHoursTemp']) if row['HeatPower'] > Limit_Heat_min and row['HeatPower'] < Limit_Heat_max 
                                        else ((Limit_Heat_max - Limit_Heat_min) / 1000 * row['sumOnHoursTemp']) if row['HeatPower'] >= Limit_Heat_max else 0,    
                                        axis=1)
    df_cum['Q_heat_basis'] = df_cum.apply(
        lambda row: (row['HeatPower'] / 1000 * row['sumOnHoursTemp']) if row['HeatPower'] > 0 and row['HeatPower'] < Limit_Heat_min else (
                    Limit_Heat_min / 1000 * row['sumOnHoursTemp']) if row['HeatPower'] >= Limit_Heat_min else 0,    axis=1
    )
    #koeling piek, midden en basislast
    df_cum['Q_cool_piek'] = df_cum.apply(lambda row: ((row['CoolPower'] - Limit_Cool_Max) / 1000 * row['sumOnHoursTemp']) if row['CoolPower'] > Limit_Cool_Max else 0, axis=1)
    df_cum['Q_cool_btwn'] = df_cum.apply(lambda row: ((row['CoolPower'] - Limit_Cool_Min) / 1000 * row['sumOnHoursTemp']) if row['CoolPower'] > Limit_Cool_Min and row['CoolPower'] < Limit_Cool_Max 
                                        else ((Limit_Cool_Max - Limit_Cool_Min) / 1000 * row['sumOnHoursTemp']) if row['CoolPower'] >= Limit_Cool_Max else 0,    
                                        axis=1)
    df_cum['Q_cool_basis'] = df_cum.apply(
        lambda row: (row['CoolPower'] / 1000 * row['sumOnHoursTemp']) if (row['CoolPower'] > 0 and row['CoolPower'] < Limit_Cool_Min) else 
                    ((Limit_Cool_Min / 1000) * row['sumOnHoursTemp']) if (row['CoolPower'] >= Limit_Cool_Min) else 0,
        axis=1
    )
    
    heat_total = round(df_cum['Q_heat_piek'].sum()) + round(df_cum['Q_heat_btwn'].sum()) + round(df_cum['Q_heat_basis'].sum())
    cool_total = round(df_cum['Q_cool_piek'].sum()) + round(df_cum['Q_cool_btwn'].sum()) + round(df_cum['Q_cool_basis'].sum())

    energy_values = [
        round(df_cum['Q_heat_piek'].sum()),
        round(df_cum['Q_cool_piek'].sum()),
        round(df_cum['Q_heat_btwn'].sum()),
        round(df_cum['Q_cool_btwn'].sum()),
        round(df_cum['Q_heat_basis'].sum()),
        round(df_cum['Q_cool_basis'].sum()),
        heat_total,cool_total,
    ]
    
    # Function to calculate y based on linear interpolation
    def calculate_integrated_hour(df, x, power_type):
        if x != 0: 
            # Find closest values above and below x in 'power_column'
            closest_below = df[df[power_type] <= x][power_type].max()
            closest_above = df[df[power_type] >= x][power_type].min()

            # Handle the edge case where x is outside the range of the column values
            if pd.isna(closest_below) or pd.isna(closest_above):
                raise ValueError(f"Value {x} is out of the interpolation range.")
             # Get the last occurrence of the closest_below and closest_above values
            if power_type == "HeatPower":
                value_below = df[df[power_type] == closest_below]['sumOnCum'].iloc[0]
                value_above = df[df[power_type] == closest_above]['sumOnCum'].iloc[0]
            elif power_type == "CoolPower":
                value_below = df[df[power_type] == closest_below]['sumOnCum'].iloc[-1]
                value_above = df[df[power_type] == closest_above]['sumOnCum'].iloc[-1]
            else:
                print(value_below)
                print(value_above)
            
            # If the closest_below and closest_above are the same, return the corresponding value
            if closest_below == closest_above:
                return value_below

            # Calculate slope (a) and intercept (b) of the linear equation y = a*x + b
            a = (value_above - value_below) / (closest_above - closest_below)
            b = value_below - a * closest_below

            # Calculate y for given x
            integrated_hour = a * x + b
        else:
            integrated_hour= 0

        return integrated_hour
    # Calculate corrosponderende punten op belastingduurkromme bij opgegeven grensen
       
    hour_max = df_cum['sumOnCum'].max()
    #koelen uur-waarden bepalen voor grenzen
    if HeatBuildingMax == 0: #check verwarmingsvraag: 
        hour_heat_low, hour_heat_high,hour_max = 0,0,0
    elif Limit_Heat_min > HeatBuildingMin: 
        hour_heat_low = calculate_integrated_hour(df_cum, Limit_Heat_min, 'HeatPower')
        hour_heat_high = calculate_integrated_hour(df_cum, Limit_Heat_max, 'HeatPower')
    else: 
        hour_heat_low = hour_max
        hour_heat_high = calculate_integrated_hour(df_cum, Limit_Heat_max, 'HeatPower')
    
    #koelen x waarde bepalen voor grenzen
    if CoolBuildingMax == 0: #check if koelvraag : 
        hour_cool_low,hour_cool_high, hour_max =0,0,0
    elif Limit_Cool_Min > CoolBuildingMin or (Limit_Cool_Min == 0 and CoolBuildingMin == 0): 
        hour_cool_low = calculate_integrated_hour(df_cum, Limit_Cool_Min, 'CoolPower')
        hour_cool_high = calculate_integrated_hour(df_cum, Limit_Cool_Max, 'CoolPower')
    elif Limit_Cool_Max < CoolBuildingMax:
        hour_cool_low = 0
        hour_cool_high = 0
    else: 
        hour_cool_low = 0
        hour_cool_high = calculate_integrated_hour(df_cum, Limit_Cool_Max, 'CoolPower')

    #Calculate Beta and Energy factors with safe division and logical checks
    if HeatBuildingMax and heat_total:
        Beta_factor_heat = min(round((Limit_Heat_max / HeatBuildingMax) * 100),100)
        Energy_factor_heat = min(round((df_cum['Q_heat_btwn'].sum() / heat_total) * 100),100)
    else:
        Beta_factor_heat = 0
        Energy_factor_heat = 0

    if CoolBuildingMax and cool_total:
        Beta_factor_cool = min(round((Limit_Cool_Max / CoolBuildingMax) * 100),100)
        Energy_factor_cool = min(round((df_cum['Q_cool_btwn'].sum() / cool_total) * 100),100)
    else:
        Beta_factor_cool = 0
        Energy_factor_cool = 0
    #Prepare output data in lists
    limit_values = [hour_heat_low,hour_heat_high,hour_cool_low, hour_cool_high, hour_max,Beta_factor_heat, Beta_factor_cool,Energy_factor_heat,Energy_factor_cool]

    
    return df_cum, limit_values, energy_values


# def generate_pdf_climate(request):
#     """
#     Builds a PDF for Tool A3: Klimaatjaar using posted canvas images + form inputs.
#     Expects a POST with 'SavePDFButton' and chart images posted as base64 strings.
#     """
#     if request.method != "POST" or 'SavePDFButton' not in request.POST:
#         return HttpResponse("Invalid request", status=400)

#     # --- helpers ---
#     def get(name, default=""):
#         return request.POST.get(name, default)

#     def decode_data_url(data_url):
#         if not data_url:
#             return None
#         try:
#             b64 = data_url.split(",", 1)[1] if "," in data_url else data_url
#             return base64.b64decode(b64)
#         except Exception:
#             return None

#     def fmt(v):
#         s = str(v)
#         return s.replace('.', ',') if (any(c.isdigit() for c in s) and '.' in s) else s

#     def safe_draw_image(cnv, img, x, y, width, height):
#         """Draw image if it exists; skip silently otherwise."""
#         if not img:
#             return
#         try:
#             cnv.drawImage(img, x, y, width=width, height=height,
#                           preserveAspectRatio=True, anchor='sw')
#         except Exception:
#             # If the image is corrupt or too big, just skip drawing it
#             pass

#     # --- gather meta ---
#     title = get("project_title", "Tool A3: Klimaatjaar")
#     user = get("username", "Onbekend")
#     stamp = datetime.now().strftime('%d %B %Y %H:%M')

#     # --- gather form values (as displayed on the page) ---
#     inputs_page1 = {
#         "Methode": get("method_text", get("method", "")),
#         "Startdag": get("startdag_text", get("startdag", "")),
#         "Startuur": get("startuur", ""),
#         "Einddag": get("einddag_text", get("einddag", "")),
#         "Einduur": get("einduur", ""),
#         "T begin [°C]": get("starttemp", ""),
#         "T eind [°C]": get("eindtemp", ""),
#         "Draaiuren [h]": get("on_hours", ""),
#         "Buiten bedrijf [h]": get("off_hours", ""),
#     }
#     inputs_page2 = {
#         "Pmax heat [kW]": get("HeatBuildingMax", ""),
#         "Pmin heat [kW]": get("HeatBuildingMin", ""),
#         "Tmax heat [°C]": get("maxTempHeat", ""),
#         "Tmin heat [°C]": get("designTempheat", ""),
#         "Pmax cool [kW]": get("CoolBuildingMax", ""),
#         "Pmin cool [kW]": get("CoolBuildingMin", ""),
#         "Tmax cool [°C]": get("maxTempCool", ""),
#         "Tmin cool [°C]": get("designTempcool", ""),
#     }
#     inputs_page3 = {
#         "Limit heat max [kW]": get("LimitHeatMax", ""),
#         "Limit heat min [kW]": get("LimitHeatMin", ""),
#         "B_f heat [%]": get("B_factor_heat", ""),
#         "E_f heat [%]": get("E_factor_heat", ""),
#         "Limit cool max [kW]": get("LimitCoolMax", ""),
#         "Limit cool min [kW]": get("LimitCoolMin", ""),
#         "B_f cool [%]": get("B_factor_cool", ""),
#         "E_f cool [%]": get("E_factor_cool", ""),
#     }

#     # --- canvases we expect from the page ---
#     chart_ids = [
#         ("Draaiuren (Donut)", "chart_myDoughnutChart"),  # stacked horizontal bar
#         ("Draaiuren vs Temp", "chart_myOnOffChart"),
#         ("Vermogen–Temperatuur", "chart_myLineChart"),
#         ("Warmtevraag (stacked)", "chart_myBarChart_heat"),
#         ("Koudevraag (stacked)", "chart_myBarChart_cool"),
#         ("Belastingduurkromme", "chart_belastingduurcurve"),
#     ]

#     charts = []
#     for entry in chart_ids:
#         if not isinstance(entry, (list, tuple)) or len(entry) < 2:
#             continue
#         label, field = entry[0], entry[1]
#         data = decode_data_url(get(field, ""))
#         if data:
#             charts.append((label, ImageReader(BytesIO(data))))

#     chart_map = dict(charts)

#     # --- setup PDF canvas ---
#     buffer = BytesIO()
#     c = canvas.Canvas(buffer)

#     styles = getSampleStyleSheet()
#     normal = styles["Normal"]
#     key_style = ParagraphStyle('key', parent=normal, fontName='Helvetica-Bold', fontSize=9, leading=11)
#     val_style = ParagraphStyle('val', parent=normal, fontName='Helvetica', fontSize=9, leading=11)

#     # --- shared table builder (consistent styling everywhere) ---
#     TABLE_GREEN = colors.HexColor("#2E7D32")  # Material-ish green
#     LIGHT_GRID = colors.HexColor("#D0D7DE")

#     def build_inputs_container(data_dict, page_width, left_margin=30, right_margin=30, header_title="Invoer"):
#         """
#         Returns a single Flowable (container Table) with two tables side-by-side,
#         consistent styling: green header, white body, alternating rows, light grid.
#         """
#         # rows for one table
#         rows = [[Paragraph(fmt(k), key_style), Paragraph(fmt(v), val_style)]
#                 for k, v in data_dict.items()]

#         # header row
#         header = [Paragraph(header_title, key_style), Paragraph("Waarde", key_style)]
#         # split evenly (header duplicated on both halves)
#         mid = (len(rows) + 1) // 2
#         left_rows = [header] + rows[:mid]
#         right_rows = [header] + rows[mid:]

#         # compute inner widths
#         inner_w = page_width - left_margin - right_margin
#         gap = 20
#         half_w = (inner_w - gap) / 2.0
#         key_col = 150
#         val_col = max(100, half_w - key_col)  # prevent negative

#         def style_table(t):
#             t.setStyle(TableStyle([
#                 # header
#                 ('BACKGROUND', (0, 0), (-1, 0), TABLE_GREEN),
#                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#FFFFFF")),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
#                 # grid + paddings
#                 ('GRID', (0, 0), (-1, -1), 0.25, LIGHT_GRID),
#                 ('LEFTPADDING', (0, 0), (-1, -1), 5),
#                 ('RIGHTPADDING', (0, 0), (-1, -1), 5),
#                 ('TOPPADDING', (0, 0), (-1, -1), 2),
#                 ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 # body backgrounds
#                 ('BACKGROUND', (0, 1), (-1, -1), colors.white),
#                 ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
#             ]))

#         left_table = Table(left_rows, colWidths=[key_col, val_col], repeatRows=1, hAlign='LEFT')
#         right_table = Table(right_rows, colWidths=[key_col, val_col], repeatRows=1, hAlign='LEFT')
#         style_table(left_table)
#         style_table(right_table)

#         container = Table([[left_table, right_table]], colWidths=[half_w, half_w])
#         container.setStyle(TableStyle([
#             ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#             ('LEFTPADDING', (0, 0), (-1, -1), 0),
#             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
#             ('TOPPADDING', (0, 0), (-1, -1), 0),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
#         ]))
#         return container

#     # ---------- PAGE 1 (Portrait) ----------
#     c.setPageSize(A4)
#     w, h = A4

#     c.setFont('Helvetica-Bold', 18)
#     c.drawCentredString(w/2, h-40, title)

#     stackedbar = chart_map.get("Draaiuren (Donut)")          # horizontal stacked bar image
#     line_img   = chart_map.get("Draaiuren vs Temp")
#     power_img  = chart_map.get("Vermogen–Temperatuur")

#     left_margin = 40
#     right_margin = 40
#     top_gap = 14
#     block_gap = 24
#     footer_min_y = 70

#     usable_w = w - left_margin - right_margin
#     y_cursor = h - 60  # start below title

#     # Charts are kept modest so a table fits
#     if stackedbar:
#         bar_h = h * 0.22
#         safe_draw_image(c, stackedbar, left_margin, y_cursor - bar_h, usable_w, bar_h)
#         y_cursor -= (bar_h + block_gap)

#     if line_img and y_cursor - (h * 0.22) > footer_min_y + 140:  # ensure room for table
#         line_h = h * 0.22
#         safe_draw_image(c, line_img, left_margin, y_cursor - line_h, usable_w, line_h)
#         y_cursor -= (line_h + block_gap)

#     if power_img and y_cursor - (h * 0.22) > footer_min_y + 140:
#         pow_h = h * 0.22
#         safe_draw_image(c, power_img, left_margin, y_cursor - pow_h, usable_w, pow_h)
#         y_cursor -= (pow_h + block_gap)

#     # Bottom: inputs_page1 table (consistent styling)
#     container1 = build_inputs_container(inputs_page1, w, left_margin, right_margin, header_title="Invoer")
#     frame_y = footer_min_y + 10
#     frame_h = max(120, (y_cursor - 10) - frame_y)  # at least some height
#     frame = Frame(left_margin, frame_y, usable_w, frame_h, showBoundary=0)
#     frame.addFromList([container1], c)

#     # Footer
#     c.setFont('Helvetica', 8)
#     c.setFillColor(colors.grey)
#     c.drawRightString(w-20, 20, "Pagina 1")
#     c.drawString(20, 20, stamp)
#     c.drawString(w/2, 20, f"Gebruiker: {user}")
#     c.showPage()

#     # ---------- PAGE 2 (Landscape) ----------
#     c.setPageSize(landscape(A4))
#     w, h = landscape(A4)

#     c.setFont('Helvetica-Bold', 16)
#     c.drawString(30, h-40, "Resultaten")

#     bel_img = chart_map.get("Belastingduurkromme")

#     left = 40
#     right = 40
#     top = 70
#     bottom = 70
#     gap_v = 28

#     inner_w = w - left - right
#     inner_h = h - top - bottom

#     chart_h = inner_h * 0.52  # leave room for table
#     if bel_img:
#         safe_draw_image(c, bel_img, left, bottom + (inner_h - chart_h), inner_w, chart_h)

#     # Table for page 2
#     container2 = build_inputs_container(inputs_page2, w, left, right, header_title="Invoer")
#     frame_y2 = bottom
#     frame_h2 = inner_h - chart_h - gap_v
#     frame2 = Frame(left, frame_y2, inner_w, max(120, frame_h2), showBoundary=0)
#     frame2.addFromList([container2], c)

#     # Footer
#     c.setFont('Helvetica', 8)
#     c.setFillColor(colors.grey)
#     c.drawRightString(w-20, 20, "Pagina 2")
#     c.drawString(20, 20, stamp)
#     c.drawString(w/2, 20, f"Gebruiker: {user}")
#     c.showPage()

#     # ---------- PAGE 3 (Landscape) ----------
#     c.setPageSize(landscape(A4))
#     w, h = landscape(A4)

#     # Top: charts side by side
#     heat_img = chart_map.get("Warmtevraag (stacked)")
#     cool_img = chart_map.get("Koudevraag (stacked)")

#     left = 40
#     right = 40
#     top = 50
#     bottom = 70
#     gap_h = 24
#     gap_cols = 24

#     inner_w = w - left - right
#     inner_h = h - top - bottom

#     col_w = (inner_w - gap_cols) / 2.0
#     chart_h = inner_h * 0.48   # top half ~48%
#     y_top = h - top - chart_h

#     if heat_img:
#         safe_draw_image(c, heat_img, left, y_top, col_w, chart_h)
#     if cool_img:
#         safe_draw_image(c, cool_img, left + col_w + gap_cols, y_top, col_w, chart_h)

#     # Bottom: inputs_page3 table
#     c.setFont('Helvetica-Bold', 14)
#     # (Optional title for bottom area)
#     # c.drawString(left, y_top - 16, "Invoer") 

#     container3 = build_inputs_container(inputs_page3, w, left, right, header_title="Invoer")
#     frame_y3 = bottom
#     frame_h3 = (y_top - gap_h) - frame_y3 if (locals().get('frame_y3') is not None) else (y_top - gap_h) - bottom
#     # fix variable if not defined earlier:
#     frame_y3 = bottom
#     frame_h3 = y_top - gap_h - frame_y3
#     frame3 = Frame(left, frame_y3, inner_w, max(120, frame_h3), showBoundary=0)
#     frame3.addFromList([container3], c)

#     # Footer
#     c.setFont('Helvetica', 8)
#     c.setFillColor(colors.grey)
#     c.drawRightString(w-20, 20, "Pagina 3")
#     c.drawString(20, 20, stamp)
#     c.drawString(w/2, 20, f"Gebruiker: {user}")
#     c.showPage()

#     # --- finish ---
#     c.save()
#     buffer.seek(0)
#     resp = HttpResponse(buffer, content_type='application/pdf')
#     resp['Content-Disposition'] = 'attachment; filename="tool_A3_klimaatjaar.pdf"'
#     return resp
def generate_pdf_climate(request):
    """
    Builds a PDF for Tool A3: Klimaatjaar using posted canvas images + form inputs.
    Expects a POST with 'SavePDFButton' and chart images posted as base64 strings.
    """
    if request.method != "POST" or 'SavePDFButton' not in request.POST:
        return HttpResponse("Invalid request", status=400)

    # --- helpers ---
    def get(name, default=""):
        return request.POST.get(name, default)

    def decode_data_url(data_url):
        if not data_url:
            return None
        try:
            b64 = data_url.split(",", 1)[1] if "," in data_url else data_url
            return base64.b64decode(b64)
        except Exception:
            return None

    def fmt(v):
        s = str(v)
        return s.replace('.', ',') if (any(c.isdigit() for c in s) and '.' in s) else s

    def safe_draw_image(cnv, img, x, y, width, height):
        """Draw image if it exists; skip silently otherwise."""
        if not img:
            return
        try:
            cnv.drawImage(img, x, y, width=width, height=height,
                          preserveAspectRatio=True, anchor='sw')
        except Exception:
            pass  # Skip corrupt/oversized images gracefully

    # --- gather meta ---
    title = get("project_title", "Tool A3: Klimaatjaar")
    user = get("username", "Onbekend")
    stamp = datetime.now().strftime('%d %B %Y %H:%M')

    # --- inputs per page ---
    inputs_page1 = {
        "Methode": get("method_text", get("method", "")),
        "Startdag": get("startdag_text", get("startdag", "")),
        "Startuur": get("startuur", ""),
        "Einddag": get("einddag_text", get("einddag", "")),
        "Einduur": get("einduur", ""),
        "T begin [°C]": get("starttemp", ""),
        "T eind [°C]": get("eindtemp", ""),
        
    }
    inputs_page1_1 = {
        "Draaiuren [h]": get("on_hours", ""),
        "Buiten bedrijf [h]": get("off_hours", ""),
    }
    inputs_page2 = {
        "Pmax heat [kW]": get("HeatBuildingMax", ""),
        "Pmin heat [kW]": get("HeatBuildingMin", ""),
        "Tmax heat [°C]": get("maxTempHeat", ""),
        "Tmin heat [°C]": get("designTempheat", ""),
        "Pmax cool [kW]": get("CoolBuildingMax", ""),
        "Pmin cool [kW]": get("CoolBuildingMin", ""),
        "Tmax cool [°C]": get("maxTempCool", ""),
        "Tmin cool [°C]": get("designTempcool", ""),
    }
    inputs_page3 = {
        "Limit heat max [kW]": get("LimitHeatMax", ""),
        "Limit heat min [kW]": get("LimitHeatMin", ""),
        "B_f heat [%]": get("B_factor_heat", ""),
        "E_f heat [%]": get("E_factor_heat", ""),
        "Limit cool max [kW]": get("LimitCoolMax", ""),
        "Limit cool min [kW]": get("LimitCoolMin", ""),
        "B_f cool [%]": get("B_factor_cool", ""),
        "E_f cool [%]": get("E_factor_cool", ""),
    }

    # --- canvases we expect from the page ---
    chart_ids = [
        ("Draaiuren (Donut)", "chart_myDoughnutChart"),     # horizontal stacked bar
        ("Draaiuren vs Temp", "chart_myOnOffChart"),
        ("Vermogen–Temperatuur", "chart_myLineChart"),
        ("Warmtevraag (stacked)", "chart_myBarChart_heat"),
        ("Koudevraag (stacked)", "chart_myBarChart_cool"),
        ("Belastingduurkromme", "chart_belastingduurcurve"),
    ]

    charts = []
    for entry in chart_ids:
        if not isinstance(entry, (list, tuple)) or len(entry) < 2:
            continue
        label, field = entry[0], entry[1]
        data = decode_data_url(get(field, ""))
        if data:
            charts.append((label, ImageReader(BytesIO(data))))
    chart_map = dict(charts)

    # --- setup PDF canvas ---
    buffer = BytesIO()
    c = canvas.Canvas(buffer)

    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    key_style = ParagraphStyle('key', parent=normal, fontName='Helvetica-Bold', fontSize=9, leading=11)
    val_style = ParagraphStyle('val', parent=normal, fontName='Helvetica', fontSize=9, leading=11)
    header_style = ParagraphStyle('thead', parent=normal, fontName='Helvetica-Bold',
                                  fontSize=9, leading=11, textColor=colors.white)

    # --- shared table builder (consistent styling everywhere, half width, LEFT aligned) ---
    TABLE_GREEN = colors.HexColor("#2E7D32")
    LIGHT_GRID = colors.HexColor("#D0D7DE")

    def build_inputs_container(data_dict, page_width, left_margin=30, right_margin=30,
                               header_title="Invoer", width_ratio=0.5):
        """
        Two-column (side-by-side) key/value tables inside a container that spans
        `width_ratio` of the usable width (default 50%), LEFT-aligned.
        """
        rows = [[Paragraph(fmt(k), key_style), Paragraph(fmt(v), val_style)]
                for k, v in data_dict.items()]

       
        # header duplicated for both halves; force white text
        header = [Paragraph(header_title, header_style), Paragraph("Waarde", header_style)]

        mid = (len(rows) + 1) // 2
        if data_dict == inputs_page1 or data_dict == inputs_page1_1:
            width_ratio = 1.0
            mid = (len(rows) ) // 2
        left_rows = [header] + rows[:mid]
        right_rows = [header] + rows[mid:]

        usable = page_width - left_margin - right_margin
        container_w = max(280, usable * width_ratio)
        gap = 16
        half_w = (container_w - gap) / 2.0
        key_col = 140
        val_col = max(90, half_w - key_col)

        def style_table(t):
            t.setStyle(TableStyle([
                # header
                ('BACKGROUND', (0, 0), (-1, 0), TABLE_GREEN),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                # grid + paddings
                ('GRID', (0, 0), (-1, -1), 0.25, LIGHT_GRID),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                # body backgrounds
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
            ]))

        left_table = Table(left_rows, colWidths=[key_col, val_col], repeatRows=1, hAlign='LEFT')
        right_table = Table(right_rows, colWidths=[key_col, val_col], repeatRows=1, hAlign='LEFT')
        style_table(left_table)
        style_table(right_table)
        column_gap = 12
        container = Table([[left_table, right_table]], colWidths=[half_w, column_gap, half_w], hAlign='LEFT')
        container.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        return container, container_w

    # Convenience for footers
    def footer(page_num, w):
        c.setFont('Helvetica', 8)
        c.setFillColor(colors.grey)
        c.drawRightString(w-20, 20, f"Pagina {page_num}")
        c.drawString(20, 20, stamp)
        c.drawString(w/2, 20, f"Gebruiker: {user}")

    # ---------- PAGE 1 (Portrait) ----------
    c.setPageSize(A4)
    w, h = A4

    c.setFont('Helvetica-Bold', 18)
    c.drawCentredString(w/2, h-36, title)

    stackedbar = chart_map.get("Draaiuren (Donut)")
    line_img   = chart_map.get("Draaiuren vs Temp")

    left_margin = 40
    right_margin = 40
    block_gap = 18
    footer_min_y = 70
    min_table_h = 80 # ensure enough space for the main table

    usable_w = w - left_margin - right_margin
    y_cursor = h - 50  # start a bit closer to title
    # Main inputs table (portrait page: full usable width, LEFT-aligned)
    container_main, cont_w_main = build_inputs_container(
        inputs_page1, w, left_margin, right_margin,
        header_title="Invoer", width_ratio=1.0  # full usable width on page 1
    )
    frame_y_main = footer_min_y + 10
    frame_h_main = max(min_table_h, (y_cursor - 10) - frame_y_main)
    frame_main = Frame(left_margin, frame_y_main, cont_w_main, frame_h_main, showBoundary=0)
    frame_main.addFromList([container_main], c)
    # Chart 2 (only if enough space remains above the main table area)
    if line_img:
        line_h = h * 0.40
        if (y_cursor - line_h) - (footer_min_y + min_table_h) >= 0:
            safe_draw_image(c, line_img, left_margin, y_cursor - line_h, usable_w, line_h)
            y_cursor -= (line_h + block_gap)
    
    # One-row info (rendered like other tables) right under Chart 1
    # inputs_page1_1 = {"Draaiuren [h]": ..., "Buiten bedrijf [h]": ...}
    container_small, cont_w_small = build_inputs_container(
        inputs_page1_1, w, left_margin, right_margin,
        header_title="Invoer", width_ratio=0.5  # half width, LEFT-aligned
    )
    small_table_h = 70  # header + 1 row fits comfortably
    frame_small = Frame(left_margin, y_cursor - small_table_h, cont_w_small, small_table_h, showBoundary=0)
    frame_small.addFromList([container_small], c)
    y_cursor = y_cursor  - block_gap  # gap after small table
    # Chart 1
    if stackedbar:
        bar_h = h * 0.14
        bar_y = y_cursor - bar_h
        safe_draw_image(c, stackedbar, left_margin, bar_y, usable_w, bar_h)
        y_cursor = bar_y - block_gap  # move below chart 1

    footer(1, w)
    c.showPage()


    # ---------- PAGE 2 (Landscape) ----------
    c.setPageSize(landscape(A4))
    w, h = landscape(A4)

    c.setFont('Helvetica-Bold', 16)
    c.drawString(30, h-40, "Vermogen–Temperatuur")

    power_img  = chart_map.get("Vermogen–Temperatuur")      # will be drawn on Page 2
 
    
    left = 40
    right = 40
    top = 70
    bottom = 70
    gap_v = 24

    inner_w = w - left - right
    inner_h = h - top - bottom

    # Draw Vermogen–Temperatuur chart here
    chart_h2 = inner_h * 0.56  # a bit taller, but leave room for table
    if power_img:
        safe_draw_image(c, power_img, left, bottom + (inner_h - chart_h2), inner_w, chart_h2)

    # Left-aligned half-width table for page 2
    container2, cont_w2 = build_inputs_container(
        inputs_page2, w, left, right, header_title="Invoer", width_ratio=0.5
    )
    frame_x2 = left  # LEFT aligned
    frame_y2 = bottom
    frame_h2 = max(120, inner_h - chart_h2 - gap_v)
    frame2 = Frame(frame_x2, frame_y2, cont_w2, frame_h2, showBoundary=0)
    frame2.addFromList([container2], c)

    footer(2, w)
    c.showPage()

    # ---------- PAGE 3 (Landscape) ----------
    c.setPageSize(landscape(A4))
    w, h = landscape(A4)

    c.setFont('Helvetica-Bold', 16)
    c.drawString(30, h-40, "Thermische Energie")

    heat_img = chart_map.get("Warmtevraag (stacked)")
    cool_img = chart_map.get("Koudevraag (stacked)")

    left = 40
    right = 40
    top = 50
    bottom = 70
    gap_h = 22
    gap_cols = 22

    inner_w = w - left - right
    inner_h = h - top - bottom

    col_w = (inner_w - gap_cols) / 2.0
    chart_h3 = inner_h * 0.48
    y_top = h - top - chart_h3

    if heat_img:
        safe_draw_image(c, heat_img, left, y_top, col_w, chart_h3)
    if cool_img:
        safe_draw_image(c, cool_img, left + col_w + gap_cols, y_top, col_w, chart_h3)

    # Left-aligned half-width table for page 3
    container3, cont_w3 = build_inputs_container(
        inputs_page3, w, left, right, header_title="Invoer", width_ratio=0.5
    )
    frame_x3 = left  # LEFT aligned
    frame_y3 = bottom
    frame_h3 = max(120, y_top - gap_h - frame_y3 if 'frame_y3' in locals() else y_top - gap_h - bottom)
    # normalize vars (no self-reference)
    frame_y3 = bottom
    frame_h3 = max(120, y_top - gap_h - frame_y3)
    frame3 = Frame(frame_x3, frame_y3, cont_w3, frame_h3, showBoundary=0)
    frame3.addFromList([container3], c)

    footer(3, w)
    c.showPage()

    # ---------- PAGE 4 (Landscape) — Belastingduurkromme ONLY ----------
    c.setPageSize(landscape(A4))
    w, h = landscape(A4)

    c.setFont('Helvetica-Bold', 16)
    c.drawString(30, h-40, "Belastingduurkromme")
    bel_img    = chart_map.get("Belastingduurkromme")        # will be drawn on Page 4
    
    left = 40
    right = 40
    top = 60
    bottom = 60
    inner_w = w - left - right
    inner_h = h - top - bottom

    if bel_img:
        safe_draw_image(c, bel_img, left, bottom, inner_w, inner_h)

    footer(4, w)
    c.showPage()

    # --- finish ---
    c.save()
    buffer.seek(0)
    resp = HttpResponse(buffer, content_type='application/pdf')
    resp['Content-Disposition'] = 'attachment; filename="tool_A3_klimaatjaar.pdf"'
    return resp

