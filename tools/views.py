from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib import messages
from django.templatetags.static import static

from .Tool_A1_Gebouwdata import gebouwgegevens
from .Tool_A3_klimaatjaar import klimaatjaar
from .Tool_W1_MollierDiagram import MollierView, generate_pdf_file
from .Tool_W2_expansievat import expansievat
from .Tool_W4_CO2verloop import CO2verloop
from .Tool_W5_buffervat import buffervat
from .models import ProjectMollier

import json, io
import pandas as pd





# inhoudsopgave pagina 
@login_required(login_url='accounts:login')
def tools(request):
    return render(request, 'tools/tools_index.html')

@method_decorator(csrf_exempt, name='dispatch')
@login_required(login_url='accounts:login')
def save_project(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            projectname = data.get('projectname')
            sessionstorage = data.get('sessionstorage')

            # Check if user already has 10 projects
            existing_projects = ProjectMollier.objects.filter(user=request.user).order_by('created_at')
            if existing_projects.count() >= 10:
                # Delete oldest project
                oldest = existing_projects.first()
                oldest.delete()

            ProjectMollier.objects.update_or_create(
                user=request.user,
                projectname=projectname,
                defaults={'sessionstorage': sessionstorage}
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@method_decorator(csrf_exempt, name='dispatch')
@login_required(login_url='accounts:login')
def load_project(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            project_id = data.get('project_id')
            project = ProjectMollier.objects.get(pk=project_id, user=request.user)

            # Save session data temporarily in Django session
            request.session['restored_sessionstorage'] = project.sessionstorage

            return JsonResponse({'status': 'ok'})
        except ProjectMollier.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Project niet gevonden'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@method_decorator(csrf_exempt, name='dispatch')
@login_required(login_url='accounts:login')
def delete_project(request):
    print("test")
    # pull from request.POST instead of request.body/JSON
    project_id = request.POST.get('project_id')
    print(project_id)
    project = get_object_or_404(ProjectMollier, id=project_id, user=request.user)

    project.delete()
    messages.success(request, "Project succesvol verwijderd.")
    # redirect back to your project‐list page
    return redirect('tools:tool_W1.html')

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
    mollierView_output = MollierView(request)
    # Get saved projects for the current user
    saved_projects = ProjectMollier.objects.filter(user=request.user).order_by('-created_at')

    # Check if we are restoring a session project
    restored_sessionstorage = request.session.pop('restored_sessionstorage', None)

    # Final render
    return render(request, 'tools/tool_W1.html', {
        'lines_RH': json.dumps(mollierView_output[0]),
        'lines_H': json.dumps(mollierView_output[1]),
        'calculated_values_start_json': json.dumps(mollierView_output[2]),
        'calculated_values_start': mollierView_output[2],
        'calculated_values_json': json.dumps(mollierView_output[3]),
        'calculated_values': mollierView_output[3],
        'process_data': mollierView_output[4],
        'warning': mollierView_output[5],  # Used for template iteration
        'process_steps': list(range(1, 5)),  # Used for template iteration
        'username': [request.user.first_name, request.user.last_name,request.user.username],
        'saved_projects': saved_projects,  # Pass projects to template
        'restored_sessionstorage': json.dumps(restored_sessionstorage) if restored_sessionstorage else None
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
# buffervat pagina
@login_required(login_url='accounts:login')
def tool_W5(request):
    buffervat_output = buffervat(request)
    return render(request, 'tools/tool_W5.html', {'buffervat_output': buffervat_output})
# thermisch vermogen pagina
@login_required(login_url='accounts:login')
def tool_W6(request):
    return render(request, 'tools/tool_W6.html')

# driefase-vermogen pagina
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

@login_required(login_url='accounts:login')
def generate_pdf(request):
    return generate_pdf_file(request)

# Whitelist allowed tools; add more as needed for the ReadME!
ALLOWED = {"INDEX","A1","A2","A3", "E1","W1","W2", "W3", "W4", "W5", "W6"}
def tool_readme(request, tool):
    code = tool.upper()
    if code not in ALLOWED:
        raise Http404("Unknown readme")

    pdf_url = static(f"tools/files/TOOL{code}-README.pdf")
    title = f"TOOL{code} – README"
    iframe_src = f"{pdf_url}#page=1&zoom=100"   # <-- was ...#view=FitH

    html = f"""<!doctype html>
            <html lang="nl">
            <head>
            <meta charset="utf-8">
            <title>{title}</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>html,body,iframe{{height:100%;margin:0}} iframe{{width:100%;border:0}}</style>
            </head>
            <body>
            <iframe src="{iframe_src}"></iframe>
            <noscript><p><a href="{pdf_url}">Download PDF</a></p></noscript>
            </body>
            </html>"""
    return HttpResponse(html)   