from django.shortcuts import render
from .Tool_A1_Gebouwdata import gebouwgegevens
from .Tool_A3_klimaatjaar import klimaatjaar
from .Tool_W1_MollierDiagram import mollierdiagram
from .Tool_W2_expansievat import expansievat
from django.contrib.auth.decorators import login_required
import json
import pandas as pd
from django.http import HttpResponse
import io

# inhoudsopgave pagina 
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
    lines_RH, lines_H, calculated_values= {},{},[]
    
    if request.method =='POST':
        Tdb_var, RH_var, Height_var = map(int, [request.POST.get('Tdb_var'), request.POST.get('RH_var'), request.POST.get('Heigth_var')])
        lines_RH, lines_H, calculated_values = mollierdiagram(Tdb_var, RH_var, Height_var)
    
    return render(request, 'tools/tool_W1.html', {
        'lines_RH': json.dumps(lines_RH),
        'lines_H': json.dumps(lines_H),
        'calculated_values': calculated_values,
    })
# expansievat pagina
@login_required(login_url='accounts:login')
def tool_W2(request):
    expansievat_ouput = expansievat(request)
    #toekomstig: je kan nog een model maken met expansievat variabelen net als adress
    return render(request, 'tools/tool_W2.html', {'expansievat_output': expansievat_ouput})



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


