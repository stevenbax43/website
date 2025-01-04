from django.shortcuts import render
from .Tool_A1_Gebouwdata import gebouwgegevens
from .Tool_A3_klimaatjaar import klimaatjaar
from .Tool_W1_MollierDiagram import mollierdiagram
from .Tool_W2_expansievat import expansievat
from .Tool_W4_CO2verloop import CO2verloop
from django.contrib.auth.decorators import login_required
import json
import pandas as pd
from django.http import HttpResponse
import io

# inhoudsopgave pagina 
@login_required(login_url='accounts:login')
def tools(request):
    return render(request, 'tools/tools_index.html')

# Gebouwgegevens pagina
@login_required(login_url='accounts:login')
def tool_A1(request):  
    adr1, EPcolor = gebouwgegevens(request)
    return render(request, 'tools/tool_A1.html', {'adr1': adr1, 'EPcolor': EPcolor})
# omrekenfactoren pagina 
@login_required(login_url='accounts:login')
def tool_A2(request):
    return render(request, 'tools/tool_A2.html')
# Klimaatjaar pagina 
@login_required(login_url='accounts:login')
def tool_A3(request):
    klimaatjaar_output = klimaatjaar(request)
    return render(request, 'tools/tool_A3.html', {
        'OnOffHours': klimaatjaar_output[0],
        'HeatCoolEnergy': klimaatjaar_output[1],
        'line_chart_data': json.dumps(klimaatjaar_output[2]),
        'line_chart_data_hoursONOFF': json.dumps(klimaatjaar_output[3]),
        'cumulative_data' : json.dumps(klimaatjaar_output[4]),
        'Limit_values': klimaatjaar_output[5],
        'energy_values':  klimaatjaar_output[6],
    })

#Mollier diagram pagina 
@login_required(login_url='accounts:login')
def tool_W1(request):
    lines_RH, lines_H, calculated_values, calculated_values_end, difference= {},{},[],[],[]
    Tdb_var_end,RH_var_end = 0,0
    if request.method =='POST':
        #start point
        Tdb_var, RH_var, Height_var = map(float, [request.POST.get('Tdb_var'), request.POST.get('RH_var'), request.POST.get('Heigth_var')])
        lines_RH, lines_H, calculated_values = mollierdiagram(Tdb_var, RH_var, Height_var)
        #end point
        Tdb_var_end, RH_var_end = map(float, [request.POST.get('Tdb_var_end'), request.POST.get('RH_var_end')])
        NoUse, NoUse2, calculated_values_end = mollierdiagram(Tdb_var_end, RH_var_end, Height_var)
        
        difference = [round(abs(Tdb_var_end-Tdb_var),1),
                      round(abs(calculated_values_end[2]-calculated_values[2]),1),
                      round(abs(calculated_values_end[0]-calculated_values[0]),1)]#[round(abs(a - b),2) for a,b in zip(calculated_values, calculated_values_end)]
    
    return render(request, 'tools/tool_W1.html', {
        'lines_RH': json.dumps(lines_RH),
        'lines_H': json.dumps(lines_H),
        'calculated_values': calculated_values,
        'calculated_values_end':calculated_values_end,
        'difference': difference,   
    })
# expansievat pagina
@login_required(login_url='accounts:login')
def tool_W2(request):
    expansievat_ouput = expansievat(request)
    return render(request, 'tools/tool_W2.html', {'expansievat_output': expansievat_ouput})

# drukverlies pagina
@login_required(login_url='accounts:login')
def tool_W3(request):
    return render(request, 'tools/tool_W3.html')

@login_required(login_url='accounts:login')
def tool_W4(request):
    CO2_output = CO2verloop(request)
    CO2_json = json.dumps(CO2_output[0])
    
    return render(request, 'tools/tool_W4.html', {'CO2_data': CO2_json})

# drukverlies pagina
@login_required(login_url='accounts:login')
def tool_E1(request):
    return render(request, 'tools/tool_E1.html')


@login_required(login_url='accounts:login')
def download_excel(request):
    if request.method == 'GET':
            df_json = request.session.get('df')
            df_Temp_json = request.session.get('df_Temp')
            df_Inputs_json = request.session.get('df_Inputs')
            # Convert JSON to DataFrame
            df = pd.DataFrame(df_json)
            df_Temp = pd.DataFrame(df_Temp_json)
            df_Inputs = pd.DataFrame(df_Inputs_json)
            
            # Generate Excel data
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_Inputs.to_excel(writer, index=False, sheet_name='Input')
                df_Temp.to_excel(writer, index=False, sheet_name='Warmte-koudevraag')
                df.to_excel(writer, index=False, sheet_name='Bedrijfsuren')

            # Rewind the buffer
            output.seek(0)

            # Create an HTTP response with the Excel file
            response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
          
            return response
    else:
        # If the method is not GET, return a 405 Method Not Allowed response
        return HttpResponse(status=405)


