import pandas as pd 
import numpy as np
import math
def mollierdiagram(Tdb_var,RH_var,Height_var):
    #voor berekenen Tdb onder 0 graden Celsius
    C1,C2,C3,C4,C5,C6,C7 = -5.6745359e3, 6.3925247,-9.6778430e-3,6.2215701e-7,2.0747825e-9,-9.4840240e-13,4.1635019
    #voor berekenen Tdb boven 0 graden Celsius
    C8,C9,C10,C11,C12,C13 = -5.8002206e3,1.3914993,-4.8640239e-2, 4.1764768e-5, -1.4452093e-8, 6.5459673
    #voor berekenen dauwpunt:
    C14, C15, C16,C17,C18= 6.54, 14.526,0.7389, 0.09486,0.4569

    #rest of constants 

    pBar = 101325*(1-2.25577e-5*Height_var)**5.256# atmospheric pressure at heigth above sea level

    # create Relative Humidity lines
    Tdb_range = np.arange(-10, 41, 1)
    RH_range = np.arange(10,110,10)
    database_RH = np.zeros((len(RH_range), len(Tdb_range)))  # Initialize matrix with zeros 

    for i, RH in enumerate(RH_range):
        for j, Tdb in enumerate(Tdb_range):
            if Tdb < 0 :  
                #formula below 0 degrees Celcius 
                part1 = 0.62198 * RH * math.exp(C1/(Tdb+273.15)+C2+C3*(Tdb+273.15)+C4*(Tdb+273.15)**2+C5*(Tdb+273.15)**3+C6*(Tdb+273.15)**4+C7*math.log(Tdb+273.15))/100
                part2 = pBar - RH * math.exp(C1/(Tdb+273.15)+C2+C3*(Tdb+273.15)+C4*(Tdb+273.15)**2+C5*(Tdb+273.15)**3+C6*(Tdb+273.15)**4+C7*math.log(Tdb+273.15))/100
            else:     
                #formula above 0 degrees Celcius 
                part1 = 0.62198 * RH * math.exp(C8/(Tdb+273.15)+C9+C10*(Tdb+273.15)+C11*(Tdb+273.15)**2+C12*(Tdb+273.15)**3+C13*math.log(Tdb+273.15))/100
                part2 = pBar - RH * math.exp(C8/(Tdb+273.15)+C9+C10*(Tdb+273.15)+C11*(Tdb+273.15)**2+C12*(Tdb+273.15)**3+C13*math.log(Tdb+273.15))/100
            outcome = part1 / part2 * 1000
            database_RH[i, j] = outcome # outcome is calculated in [g/kg] watervapor [g] in one [kg] of air. 
    #make the numpy array an dataframe pandas 
    dataframe_RH = pd.DataFrame(database_RH.T, columns=RH_range, index=Tdb_range) #transpose database_RH 
  
    
    #create Enthalpy lines 
    H_range = np.arange(-5,95,5) # unit in [kJ/kG] 
    df_enthalpy = pd.DataFrame(H_range, columns=['H_range'])
    df_enthalpy['T_0'] = df_enthalpy['H_range']/1.006    # something weird in the formulas 
    df_enthalpy['T_100'] = [-9.21,-5.75,-2.58,0.33,3.125,5.71,8.1,10.306,12.36,14.27,16.05,17.718,19.28,20.753,22.14,23.45,24.692,25.87,26.992,28.06] #wet-bulb temp

    #get the calculated [g/kg] from the 100% RH database
    RH_100 = database_RH[-1] #this is the 100% list
    df_enthalpy['RH_100_interpolated'] = [np.interp(T, Tdb_range, RH_100) for T in df_enthalpy['T_100']]
    
    #Calculate extra parameters  
    Tdb_var_K = Tdb_var + 273.15
    if Tdb_var < 0:
        #pws is the saturated partiele dampdruk/dampspanning. 
        pws = math.exp(C1/(Tdb_var_K) + C2+ C3 * Tdb_var_K +C4*Tdb_var_K**2 +C5*Tdb_var_K**3+C6*Tdb_var_K**4+C7*math.log(Tdb_var_K))
    else:
        pws = math.exp(C8/(Tdb_var_K) + C9+ C10 * Tdb_var_K +C11*Tdb_var_K**2 +C12*Tdb_var_K**3+C13*math.log(Tdb_var_K))
    AH = ((0.62198* RH_var * pws/100)/(pBar-RH_var*pws/100))*1000 #g/kg is de abs. vochtigheid op basis van invoer
    pw = (pBar*AH/1000)/(0.62198+AH/1000) #partial pressure at RH given (Not saturated)
    
    if Tdb_var < 0:
        #Td is de dauwpunt temperatuur
        Td = 6.09+12.608*math.log(pw/1000)+0.4959*math.log(pw/1000)**2
    else:
        Td = C14 +C15*math.log(pw/1000)+C16*math.log(pw/1000)**2+C17*math.log(pw/1000)**3+C18*(pw/1000)**0.1984
    
    H = (1006*Tdb_var+AH*(2500.77+Tdb_var*1.82))/1000 # kJ/kG enthalpy op basis van invoer
    V = 0.2871* Tdb_var_K*(1+1.6078*AH/1000)/(pBar/1000) #specific Volume (rho) op basis van invoer
    rho = 1/V # density (rho) op basis van invoeer
    
    calculated_values = [round(AH,1), round(pws), round(H,1), V, round(rho,2), round(pw), round(Td,1), round(pBar)]
   
    #prepare data for views.py 
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



    return  lines_RH, lines_H, calculated_values