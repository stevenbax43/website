import numpy as math

def CO2verloop(request):
 
    lst_C_t, lst_C_t_o, CO2_list= [], [], {}
    ruimteinhoud, ventilatiehoeveelheid_pp,CO2productie_pp,aantal_personen,bezetting,buitenluchtkwaliteit,beginconcentratie,tijd = 0,0,0,0,0,0,0,0
    if request.method =='POST':
        ruimteinhoud, ventilatiehoeveelheid_pp = map(float, [request.POST.get('volume_room'), request.POST.get('ventilation_pp')])
        CO2productie_pp, aantal_personen = map(float,[request.POST.get('production_pp'), request.POST.get('number_persons')])
        bezetting, buitenluchtkwaliteit = map(float,[request.POST.get('bezetting'), request.POST.get('outsite_air_ppm')])
        beginconcentratie, tijd = map(float,[request.POST.get('start_ppm'), request.POST.get('time_hour')])

        #omrekenen 
        time_unit = tijd * 3600 
        CO2_productie_pp_unit = CO2productie_pp /1000 /3600 #m3/h per persoon
        C_ex_unit = buitenluchtkwaliteit /1000000 #parts per million naar parts m3gas/m3
        C_o_unit = beginconcentratie / 1000000 #parts per million naar parts m3gas/m3
        Ventilatie_hoeveelheid = ventilatiehoeveelheid_pp * aantal_personen / 3600 #m3/s
        CO2_productie_unit = CO2_productie_pp_unit * bezetting/100 * aantal_personen #m3/s
     
        #berkenen 
        C_t_end = (CO2_productie_unit*1e6)/Ventilatie_hoeveelheid+buitenluchtkwaliteit-(CO2_productie_unit*1e6/Ventilatie_hoeveelheid-beginconcentratie+buitenluchtkwaliteit)*math.exp(-Ventilatie_hoeveelheid/ruimteinhoud*time_unit)
        
        #voorbereiden graph
        #berekening voor grafiek 
        step = 0.05 #in 
        lst = [round(i * step, 2) for i in range(int(tijd/step) + 1)] #in 20 stappen met tijd 
        
        for item in lst:
            item_sec = item *3600
            C_t = (CO2_productie_unit*1e6)/Ventilatie_hoeveelheid+buitenluchtkwaliteit-(CO2_productie_unit*1e6/Ventilatie_hoeveelheid-beginconcentratie+buitenluchtkwaliteit)*math.exp(-Ventilatie_hoeveelheid/ruimteinhoud*item_sec)
            lst_C_t.append(round(C_t))
            lst_C_t_o.append(round(C_t - beginconcentratie))


        #create list for chartdata in HTML 
        CO2_list = {
        'x_values': lst,  # X-axis values from 0 to 40
        'C_t_curve': lst_C_t,  # Dataset 1 y-axis values
        'C_t_o_curve': lst_C_t_o,   # Dataset 2 y-axis values
        }
    return  [CO2_list]
