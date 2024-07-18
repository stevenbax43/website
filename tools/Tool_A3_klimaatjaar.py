import pandas as pd 
import numpy as np
from datetime import datetime

def klimaatjaar(request):
    
    OnOffHours, HeatCoolEnergy, line_chart_data, line_chart_data_hoursONOFF, cumulative_data,limit_values, energy_values = [], [], {}, {},{}, [], []
    designTempheat, maxTempHeat,HeatPowerMax, HeatPowerMin,designTempcool, maxTempCool, CoolPowerMax,CoolPowerMin = 0,0,0,0,0,0,0,0

    if request.method =='POST':
        startdag, einddag = map(int, [request.POST.get('startdag'), request.POST.get('einddag')])
        startuur, einduur = map(int,[request.POST.get('startuur'), request.POST.get('einduur')])
        method = request.POST.get('method')
  
        OnOffHours, df_Temp, df= OnOffTime(startdag,einddag,startuur,einduur, method)
        
        #print(df_json)
        designTempheat, maxTempHeat, HeatPowerMax, HeatPowerMin = map(int, [
            request.POST.get('designTempheat'), request.POST.get('maxTempHeat'), request.POST.get('HeatPowerMax'), request.POST.get('HeatPowerMin')])
        designTempcool, maxTempCool, CoolPowerMax, CoolPowerMin = map(int, [
            request.POST.get('designTempcool'), request.POST.get('maxTempCool'), request.POST.get('CoolPowerMax'), request.POST.get('CoolPowerMin')])
        HeatCoolEnergy, df_Temp = PowerEnergy(df_Temp, designTempheat, maxTempHeat, HeatPowerMax,HeatPowerMin, designTempcool, maxTempCool, CoolPowerMax, CoolPowerMin)
        

        #cumulative belastingduurkromme maken. 
        maxPowerHeat, minPowerHeat, maxPowerCool, minPowerCool = map(int, [
            request.POST.get('maxPowerHeat'), request.POST.get('minPowerHeat'), request.POST.get('maxPowerCool'),request.POST.get('minPowerCool') ])
             
        df_cum, limit_values, energy_values = cumulative_graph(df_Temp, maxPowerHeat,minPowerHeat,maxPowerCool,minPowerCool, HeatPowerMin,CoolPowerMin, HeatPowerMax, CoolPowerMax)

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
            'HeatPowerMax': [HeatPowerMax],
            'OntwerpTempCool': [designTempcool],
            'maxTempCool': [maxTempCool],
            'CoolPowerMax': [CoolPowerMax]
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
        'OffHours': df_Temp['sumOffTemp'].tolist(),   # Dataset 2 y-axis values
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

def OnOffTime(startday,endday,starthour,endhour, method):
    df = pd.DataFrame()
    if int(method) == 1:
        df = pd.read_csv('tools/static/tools/files/Klimaatjaar2023deBilt.csv', sep=';')
    elif int(method) == 2:
        df = pd.read_csv('tools/static/tools/files/Klimaatjaar2018deBilt.csv', sep=';')
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
    OnTimeHours = df_Temp['sumOnTemp'].sum()
    OffTimeHours = df_Temp['sumOffTemp'].sum()
    OnOffHours = [OnTimeHours, OffTimeHours]
  

    return OnOffHours, df_Temp, df

def PowerEnergy(df_Temp,designTempheat,maxTempHeat,HeatPowerMax,HeatPowerMin, designTempcool,maxTempCool,CoolPowerMax, CoolPowerMin):
    #Vermogen & Energie 
    #bereken stooklijn verwarmen

    slopeHeat = (HeatPowerMax-HeatPowerMin) / ((designTempheat)-maxTempHeat)
    interceptHeat = HeatPowerMax - slopeHeat * (designTempheat)
    df_Temp['HeatPower'] = np.where((df_Temp['TempRange'] >= designTempheat) & (df_Temp['TempRange'] <= maxTempHeat ),
                                    slopeHeat * df_Temp['TempRange'] + interceptHeat,
                                    np.where(df_Temp['TempRange'] < designTempheat, HeatPowerMax, HeatPowerMin)).round(2)
    df_Temp['Q_heat[MWh]'] = (df_Temp['HeatPower']/1000 * df_Temp['sumOnTemp']).round(2)
    HeatEnergy = df_Temp['Q_heat[MWh]'].sum()

    #bereken stooklijn koelen

    slopeCool = (CoolPowerMax-CoolPowerMin) / ((maxTempCool)-designTempcool)
    interceptCool = CoolPowerMax - slopeCool * (maxTempCool)
    df_Temp['CoolPower'] = np.where((df_Temp['TempRange'] >= designTempcool) & (df_Temp['TempRange'] <= maxTempCool ),
                                    slopeCool * df_Temp['TempRange'] + interceptCool,
                                    np.where(df_Temp['TempRange'] < designTempcool, CoolPowerMin,CoolPowerMax)).round(1)

    df_Temp['Q_cool[MWh]'] = (df_Temp['CoolPower']/1000 * df_Temp['sumOnTemp']).round(1)
    CoolEnergy = df_Temp['Q_cool[MWh]'].sum()
    HeatCoolEnergy = [round(HeatEnergy), round(CoolEnergy)]
    #print(df_Temp)
    #prepare line_chart_data


    return HeatCoolEnergy, df_Temp

def cumulative_graph(df_Temp, maxPowerHeat, minPowerHeat, maxPowerCool, minPowerCool, HeatPowerMin,CoolPowerMin, HeatPowerMax, CoolPowerMax):
    #bereken belastingduurkromme 
    df_cum = df_Temp 
    df_cum['sumOnCum'] = df_cum['sumOnTemp'].cumsum()
    #verwarmen piek, midden en basislast
    df_cum['Q_heat_piek'] = df_cum.apply(lambda row: ((row['HeatPower'] - maxPowerHeat) / 1000 * row['sumOnTemp']) if row['HeatPower'] > maxPowerHeat else 0, axis=1)
    df_cum['Q_heat_btwn'] = df_cum.apply(lambda row: ((row['HeatPower'] - minPowerHeat) / 1000 * row['sumOnTemp']) if row['HeatPower'] > minPowerHeat and row['HeatPower'] < maxPowerHeat 
                                        else ((maxPowerHeat - minPowerHeat) / 1000 * row['sumOnTemp']) if row['HeatPower'] >= maxPowerHeat else 0,    
                                        axis=1)
    df_cum['Q_heat_basis'] = df_cum.apply(
        lambda row: (row['HeatPower'] / 1000 * row['sumOnTemp']) if row['HeatPower'] > 0 and row['HeatPower'] < minPowerHeat else (
                    minPowerHeat / 1000 * row['sumOnTemp']) if row['HeatPower'] >= minPowerHeat else 0,    axis=1
    )
    #koeling piek, midden en basislast
    df_cum['Q_cool_piek'] = df_cum.apply(lambda row: ((row['CoolPower'] - maxPowerCool) / 1000 * row['sumOnTemp']) if row['CoolPower'] > maxPowerCool else 0, axis=1)
    df_cum['Q_cool_btwn'] = df_cum.apply(lambda row: ((row['CoolPower'] - minPowerCool) / 1000 * row['sumOnTemp']) if row['CoolPower'] > minPowerCool and row['CoolPower'] < maxPowerCool 
                                        else ((maxPowerCool - minPowerCool) / 1000 * row['sumOnTemp']) if row['CoolPower'] >= maxPowerCool else 0,    
                                        axis=1)
    df_cum['Q_cool_basis'] = df_cum.apply(
        lambda row: (row['CoolPower'] / 1000 * row['sumOnTemp']) if (row['CoolPower'] > 0 and row['CoolPower'] < minPowerCool) else 
                    ((minPowerCool / 1000) * row['sumOnTemp']) if (row['CoolPower'] >= minPowerCool) else 0,
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
    #koelen x waarde bepalen voor grenzen
    if HeatPowerMax == 0: #check verwarmingsvraag: 
        hour_heat_low, hour_heat_high,hour_max = 0,0,0
    elif minPowerHeat > HeatPowerMin: 
        hour_heat_low = calculate_integrated_hour(df_cum, minPowerHeat, 'HeatPower')
        hour_heat_high = calculate_integrated_hour(df_cum, maxPowerHeat, 'HeatPower')
    else: 
        hour_heat_low = hour_max
        hour_heat_high = calculate_integrated_hour(df_cum, maxPowerHeat, 'HeatPower')
    
    #koelen x waarde bepalen voor grenzen
    if CoolPowerMax == 0: #check if koelvraag : 
        hour_cool_low,hour_cool_high, hour_max =0,0,0
    elif minPowerCool > CoolPowerMin: 
        hour_cool_low = calculate_integrated_hour(df_cum, minPowerCool, 'CoolPower')
        hour_cool_high = calculate_integrated_hour(df_cum, maxPowerCool, 'CoolPower')
    else: 
        hour_cool_low = 0
        hour_cool_high = calculate_integrated_hour(df_cum, maxPowerCool, 'CoolPower')
        
    
    #Prepare output data in lists
    limit_values = [hour_heat_low,hour_heat_high,hour_cool_low, hour_cool_high, hour_max]
    
    
    return df_cum, limit_values, energy_values