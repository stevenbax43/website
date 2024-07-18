import pandas as pd 
import numpy as np
import math
import time 

start_time = time.time()
#voor berekenen Tdb onder 0 graden Celsius
C1,C2,C3,C4,C5,C6,C7 = -5.6745359e3, 6.3925247,-9.6778430e-3,6.2215701e-7,2.0747825e-9,-9.4840240e-13,4.1635019
#voor berekenen Tdb boven 0 graden Celsius
C8,C9,C10,C11,C12,C13 = -5.8002206e3,1.3914993,-4.8640239e-2, 4.1764768e-5, -1.4452093e-8, 6.5459673
#voor berekenen dauwpunt:
C14, C15, C16,C17,C18= 6.54, 14.526,0.7389, 0.09486,0.4569

#rest of constants 
pBar = 101325 # atmospheric pressure at 0m above sea level

#variables 
Tdb_var = 30 # degrees Celsius 
RH_var = 60 # %
# create Relative Humidity lines
Tdb_range = np.arange(-10, 41, 1)
RH_range = np.arange(10,110,10)
database = np.zeros((len(RH_range), len(Tdb_range)))  # Initialize matrix with zeros 

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
        database[i, j] = outcome # outcome is calculated in [g/kg] watervapor [g] in one [kg] of air. 

#create Enthalpy lines 
H_range = np.arange(-5,95,5) # unit in [kJ/kG] 
df_enthalpy = pd.DataFrame(H_range, columns=['H_range'])
df_enthalpy['T_0'] = df_enthalpy['H_range']/1.006    # something weird in the formulas 
df_enthalpy['T_100'] = [-9.21,-5.75,-2.58,0.33,3.125,5.71,8.1,10.306,12.36,14.27,16.05,17.718,19.28,20.753,22.14,23.45,24.692,25.87,26.992,28.06] #wet-bulb temp

#get the calculated [g/kg] from the 100% RH database
RH_100 = database[-1] #this is the 100% list
df_enthalpy['RH_100_interpolated'] = [np.interp(T, Tdb_range, RH_100) for T in df_enthalpy['T_100']]

#Calculate extra parameters  
Tdb_var_K = Tdb_var + 273.15
if Tdb_var < 0:
    pws = math.exp(C1/(Tdb_var_K) + C2+ C3 * Tdb_var_K +C4*Tdb_var_K**2 +C5*Tdb_var_K**3+C6*Tdb_var_K**4+C7*math.log(Tdb_var_K))
else:
    pws = math.exp(C8/(Tdb_var_K) + C9+ C10 * Tdb_var_K +C11*Tdb_var_K**2 +C12*Tdb_var_K**3+C13*math.log(Tdb_var_K))
W = ((0.62198* RH_var * pws/100)/(pBar-RH_var*pws/100))*1000 #g/kg
h = (1006*Tdb_var+W*(2500.77+Tdb_var*1.82))/1000 # kJ/kG enthalpy 
print(Tdb_var_K)
print(W)
print(pBar)
V = 0.2871* Tdb_var_K*(1+1.6078*W/1000)/(pBar/1000) #specific Volume
print(V)
rho = 1/V # density
print(rho)
pw = (pBar*W/1000)/(0.62198+W/1000) #partial pressure 
if Tdb_var < 0:
    Td = 6.09+12.608*math.log(pw/1000)+0.4959*math.log(pw/1000)**2
else:
    Td = C14 +C15*math.log(pw/1000)+C16*math.log(pw/1000)**2+C17*math.log(pw/1000)**3+C18*(pw/1000)**0.1984

#square input 
square_x1,square_x2  = 0, Tdb_var
square_y1, square_y2 = W, Tdb_var


end_time = time.time()


# Calculate compute time
compute_time = end_time - start_time

# Print the compute time
print("Compute time:", compute_time, "seconds")