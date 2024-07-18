import math
def expansievat(request): 
    Temp_aanvoer, Temp_retour, Temp_average, input_sys_inhoud, expansion_volume,CV_volume_norm = 0,0,0,0,0,0
    einddruk, voordruk_input,st_height, nuttig_effect, bruto_vessel, volume_advies, vermogen, voordruk =0,0,0,0,0,0,0,0
    based_on_voor, based_on_sys = '',''
    locatie_toggle = False
    VolumeExpansionPercentage, CVInstallatieValues,expansievat_output= [], [], []
    if request.method =='POST':
        
        Temp_aanvoer, Temp_retour, input_sys_inhoud = map(int, [request.POST.get('temp_aanvoer'), request.POST.get('temp_retour'),  request.POST.get('sys_inhoud')])
        einddruk, voordruk_input, st_height, vermogen = map(float,[request.POST.get('einddruk'), request.POST.get('voordruk'), request.POST.get('st_height'),request.POST.get('vermogen')])
        
                                                                     
        CV_keuze = int(request.POST.get('CVInstallatie'))
        
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
        #pak de grootste waarde
        if calc_sys_inhoud > input_sys_inhoud:
            sys_inhoud = calc_sys_inhoud
            based_on_sys = '*Berekend op basis van vermogen & CV keuze'
        else: 
            sys_inhoud = input_sys_inhoud
            based_on_sys = '*Berekend op basis van systseeminhoud input'
        
        #bepaal inhoud vat op basis van input waarde
        Temp_average = int((Temp_aanvoer + Temp_retour) /2)
        VolumeExpansionPercentage = [(25, 0.35),(30, 0.43),(35, 0.63),(40, 0.75),(45, 0.96),(50, 1.18),(55, 1.42),(60, 1.68),(70, 2.25),(80, 2.89),(90, 3.58),(100, 4.34),(110, 5.16)]
        closest_index_exp = min(range(len(VolumeExpansionPercentage)), key=lambda i: abs(VolumeExpansionPercentage[i][0] - Temp_average))
        expansion_percentage = VolumeExpansionPercentage[closest_index_exp][1]
        expansion_volume = round(((expansion_percentage/100) * sys_inhoud),2)

        nuttig_effect = round(((einddruk+1) - (voordruk_input+1))/(einddruk+1),2)
        bruto_vessel = round((expansion_volume * 1.25) / nuttig_effect ,1)
        volume_advies = math.ceil((bruto_vessel)/5) *5

        # bepaal statische voordruk
        voordruk_static = (st_height * 0.1) + 0.3 # statische hoogte 1 meter waterkolom = 0.1 bar. Met 0.3 bar veiligheidsmarge
        if voordruk_static > voordruk_input: # als de statische berekende voordruk groter is dat de gekozen voordruk, kies een hogere voordruk
            
            data_voordruk = {0.5,1.0,1.5,2.0,2.5,3}
            voordruk = next((value for value in data_voordruk if value >= voordruk_static), None)
            based_on_voor = '*Berekend op basis van berekende statische voordruk'
        else:
            voordruk = voordruk_input
            based_on_voor = '*Berekend op basis van voordruk input'
        
        
        expansievat_output = [Temp_average, nuttig_effect, bruto_vessel, volume_advies, voordruk, based_on_sys, based_on_voor, expansion_percentage,
                              round(expansion_volume,1), Temp_aanvoer, Temp_retour,einddruk ,input_sys_inhoud, round(sys_inhoud), round(st_height),CV_volume_norm,locatie_toggle ]   
        
    return expansievat_output