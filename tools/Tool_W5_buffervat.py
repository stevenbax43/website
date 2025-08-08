import math
def buffervat(request): 
    Vermogen_min, Temp_verschil, tijd_aan, soortelijke_warmte,dichtheid= 0,0,0,0,0
    buffervat_output = []
    if request.method =='POST':
        
        Vermogen_min, Temp_verschil, tijd_aan = map(int, [request.POST.get('min_vermogen'), request.POST.get('temp_verschil'),  request.POST.get('tijd_aan')])
        soortelijke_warmte, dichtheid  = map(float,[request.POST.get('soortelijke_warmte'), request.POST.get('dichtheid')])
        
        Volume_L = 1000* (Vermogen_min * tijd_aan * 60 ) / (dichtheid *Temp_verschil * soortelijke_warmte ) 
                                                                     
        
        
        buffervat_output = [round(Volume_L), Vermogen_min, Temp_verschil, tijd_aan, soortelijke_warmte, round(dichtheid) ]   
        
    return buffervat_output