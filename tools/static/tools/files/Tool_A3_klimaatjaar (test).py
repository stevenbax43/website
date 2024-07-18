import pandas as pd 
import numpy as np


df = pd.read_csv('klimaatjaar2018deBilt.csv', sep=';')
df['YYYYMMDD'] = pd.to_datetime(df['YYYYMMDD'], format='%Y%m%d')
df['day_of_week'] = df['YYYYMMDD'].dt.dayofweek+1

#aanname:   1 januari is een maandag. 
startday = 1
endday = 5
starthour = 7
endhour = 19

# werkdagen en daguren in range van input
df['within_range_day'] = df['day_of_week'].apply(lambda x: 1 if startday <= x <= endday else 0)
df['within_range_hour'] = df['HH'].apply(lambda x: 1 if starthour <= x <= endhour else 0)

#bedrijfssituatie ON/OFF
df['onTime'] = df['within_range_day'] * df['within_range_hour']
df['onTemp'] = df.apply(lambda row: row['T']/10 if row['onTime'] == 1 else np.nan, axis=1)
df['offTemp'] = df.apply(lambda row: row['T']/10 if row['onTime'] == 0 else np.nan, axis=1)

#input temperatuur 
lowTemp = -20
highTemp = 40
df_Temp = pd.DataFrame({'TempRange': range(lowTemp, highTemp + 1)})
df_Temp['sumOnTemp'] = df_Temp['TempRange'].apply(lambda x: ((df['onTemp'] < x) & (df['onTemp'] >= x-1)).sum())
df_Temp['sumOffTemp'] = df_Temp['TempRange'].apply(lambda x: ((df['offTemp'] < x) & (df['offTemp'] >= x-1)).sum())
OnTimeHours = df_Temp['sumOnTemp'].sum()
OffTimeHours = df_Temp['sumOffTemp'].sum()

#Vermogen & Energie 
#bereken stooklijn verwarmen
minTempHeat = -10 #ontwerptemperatuur 
maxTempHeat = 16
HeatPowerMax = 150 # op min temp 
HeatPowerMin = 0 
slopeHeat = (HeatPowerMax-HeatPowerMin) / ((minTempHeat)-maxTempHeat)
interceptHeat = HeatPowerMax - slopeHeat * (minTempHeat)
df_Temp['HeatPower'] = np.where((df_Temp['TempRange'] >= minTempHeat) & (df_Temp['TempRange'] <= maxTempHeat ),
                                   slopeHeat * df_Temp['TempRange'] + interceptHeat,
                                   np.where(df_Temp['TempRange'] < minTempHeat, HeatPowerMax, HeatPowerMin)).round(2)
df_Temp['Q_heat[MWh]'] = (df_Temp['HeatPower']/1000 * df_Temp['sumOnTemp']).round(2)
HeatEnergy = df_Temp['Q_heat[MWh]'].sum()

#bereken stooklijn koelen
minTempCool = 10
maxTempCool = 40 #ontwerpTemperatuur! 
CoolPowerMax = 100 # op min temp cool
CoolPowertMin = 0
slopeCool = (CoolPowerMax-CoolPowertMin) / ((maxTempCool)-minTempCool)
interceptCool = CoolPowerMax - slopeCool * (maxTempCool)
df_Temp['CoolPower'] = np.where((df_Temp['TempRange'] >= minTempCool) & (df_Temp['TempRange'] <= maxTempCool ),
                                   slopeCool * df_Temp['TempRange'] + interceptCool,
                                   np.where(df_Temp['TempRange'] < minTempCool, CoolPowertMin,CoolPowerMax)).round(1)

df_Temp['Q_cool[MWh]'] = (df_Temp['CoolPower']/1000 * df_Temp['sumOnTemp']).round(1)
CoolEnergy = df_Temp['Q_cool[MWh]'].sum()

#bereken belastingduurkromme (Cumalative graph)
df_cum = df_Temp 
df_cum['sumOnCum'] = df_cum['sumOnTemp'].cumsum()

maxPowerHeat = 60 #kW maximale waarde in belastingduurkromme voor verwamen
minPowerHeat = 30 #kW minimale waarde in belastingduurkromme voor verwamen
maxPowerCool = 42 #kW maximale waarde in belastingduurkromme voor koelen
minPowerCool = 20 #kW minimale waarde in belastingduurkromme voor koelen


df_cum['Q_heat_piek'] = df_cum.apply(lambda row: ((row['HeatPower'] - maxPowerHeat) / 1000 * row['sumOnTemp']) if row['HeatPower'] > maxPowerHeat else 0, axis=1)
df_cum['Q_heat_btwn'] = df_cum.apply(lambda row: ((row['HeatPower'] - minPowerHeat) / 1000 * row['sumOnTemp']) if row['HeatPower'] > minPowerHeat and row['HeatPower'] < maxPowerHeat 
                                     else ((maxPowerHeat - minPowerHeat) / 1000 * row['sumOnTemp']) if row['HeatPower'] >= maxPowerHeat else 0,    
                                     axis=1)
df_cum['Q_heat_basis'] = df_cum.apply(
    lambda row: (row['HeatPower'] / 1000 * row['sumOnTemp']) if row['HeatPower'] > 0 and row['HeatPower'] < minPowerHeat else (
                minPowerHeat / 1000 * row['sumOnTemp']) if row['HeatPower'] >= minPowerHeat else 0,    axis=1
)
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
#Prepare output data in lists
energy_values = [
    round(df_cum['Q_heat_piek'].sum()),
    round(df_cum['Q_cool_piek'].sum()),
    round(df_cum['Q_heat_btwn'].sum()),
    round(df_cum['Q_cool_btwn'].sum()),
    round(df_cum['Q_heat_basis'].sum()),
    round(df_cum['Q_cool_basis'].sum()),
    heat_total,cool_total,
]
print(energy_values)
# Function to calculate y based on linear interpolation
def calculate_y(df, x, power_type):
    # Determine which power column to use
    if power_type == 'HeatPower':
        power_column = 'HeatPower'
    elif power_type == 'CoolPower':
        power_column = 'CoolPower'
    else:
        raise ValueError("Invalid power_type. Use 'HeatPower' or 'CoolPower'.")

    # Find closest values above and below x in 'power_column'
    closest_below = df[df[power_column] < x][power_column].max()
    closest_above = df[df[power_column] > x][power_column].min()

    # Get corresponding values in 'sumOnCum'
    row_closest_below = df[df[power_column] == closest_below]
    value_closest_below_sumOnCum = row_closest_below['sumOnCum'].iloc[0]

    row_closest_above = df[df[power_column] == closest_above]
    value_closest_above_sumOnCum = row_closest_above['sumOnCum'].iloc[0]

    # Calculate slope (a) and intercept (b) of the linear equation y = a*x + b
    a = (value_closest_above_sumOnCum - value_closest_below_sumOnCum) / (closest_above - closest_below)
    b = value_closest_above_sumOnCum - a * closest_above

    # Calculate y for given x
    y = a * x + b

    return y
# Calculate y for x = 5 using HeatPower
x1_heat = calculate_y(df_cum, minPowerHeat, 'HeatPower')
x2_heat = calculate_y(df_cum, maxPowerHeat, 'HeatPower')

# Calculate y for x = 30 using HeatPower
x1_cool = calculate_y(df_cum, minPowerCool, 'CoolPower')
x2_cool = calculate_y(df_cum, maxPowerCool, 'CoolPower')
x3_max = df_cum['sumOnCum'].max()
