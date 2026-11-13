from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse, Http404
from django.templatetags.static import static
from tools.models import ProjectMollier, SfbClass
from django.db.models import Q 
from tools.services.sfb_scoring import analyse_search_term

from .Tool_A1_Gebouwdata import gebouwgegevens
from .Tool_A3_klimaatjaar import klimaatjaar, generate_pdf_climate
from .Tool_A4_NLsfB import get_children
from .Tool_W1_MollierDiagram import MollierView, generate_pdf_mollier
from .Tool_W2_expansievat import build_pressure_height_diagram, expansievat
from .Tool_W4_CO2verloop import CO2verloop, generate_pdf_CO2
from .Tool_W5_buffervat import buffervat


import json, io, math
import pandas as pd

# inhoudsopgave pagina 
@login_required(login_url='accounts:login')
def tools(request):
    return render(request, 'tools/tools_index.html')

@method_decorator(csrf_exempt, name='dispatch')
@login_required(login_url='accounts:login')
def save_project(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Ongeldige JSON'}, status=400)
    if not isinstance(data, dict):
        return JsonResponse({'status': 'error', 'message': 'Ongeldige projectgegevens'}, status=400)

    projectname = data.get('projectname')
    sessionstorage = data.get('sessionstorage')
    if not isinstance(projectname, str) or not projectname.strip():
        return JsonResponse({'status': 'error', 'message': 'Projectnaam ontbreekt'}, status=400)
    if not isinstance(sessionstorage, dict):
        return JsonResponse({'status': 'error', 'message': 'Projectgegevens ontbreken'}, status=400)

    project, created = ProjectMollier.objects.update_or_create(
        user=request.user,
        projectname=projectname.strip(),
        defaults={'sessionstorage': sessionstorage},
    )
    if created:
        projects = ProjectMollier.objects.filter(user=request.user).order_by('created_at')
        if projects.count() > 10:
            projects.exclude(pk=project.pk).first().delete()
    return JsonResponse({
        'status': 'success',
        'project_id': project.pk,
        'projectname': project.projectname,
    })

@method_decorator(csrf_exempt, name='dispatch')
@login_required(login_url='accounts:login')
def load_project(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Ongeldige JSON'}, status=400)
    if not isinstance(data, dict):
        return JsonResponse({'status': 'error', 'message': 'Ongeldige projectgegevens'}, status=400)

    project_id = data.get('project_id')
    if isinstance(project_id, bool) or not str(project_id).isdigit():
        return JsonResponse({'status': 'error', 'message': 'Project niet gevonden'}, status=404)
    try:
        project = ProjectMollier.objects.get(
            pk=project_id,
            user=request.user,
        )
    except (ProjectMollier.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'status': 'error', 'message': 'Project niet gevonden'}, status=404)

    request.session['restored_sessionstorage'] = project.sessionstorage
    return JsonResponse({'status': 'ok'})

@method_decorator(csrf_exempt, name='dispatch')
@login_required(login_url='accounts:login')
def delete_project(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Ongeldige JSON'}, status=400)
    if not isinstance(data, dict):
        return JsonResponse({'status': 'error', 'message': 'Ongeldige projectgegevens'}, status=400)

    project_id = data.get('project_id')
    if isinstance(project_id, bool) or not str(project_id).isdigit():
        return JsonResponse({'status': 'error', 'message': 'Project niet gevonden'}, status=404)
    deleted, _ = ProjectMollier.objects.filter(
        id=project_id,
        user=request.user,
    ).delete()
    if not deleted:
        return JsonResponse({'status': 'error', 'message': 'Project niet gevonden'}, status=404)
    return JsonResponse({'status': 'deleted'})

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
        'username': [request.user.first_name, request.user.last_name,request.user.username],
    })



@login_required(login_url='accounts:login')
def tool_A4(request):
   
    root_classes = SfbClass.objects.filter(parent__isnull=True)
    return render(request, "tools/tool_A4.html", {"classes": root_classes})


#Mollier diagram pagina 
@login_required(login_url='accounts:login')
def tool_W1(request):
    mollierView_output = MollierView(request)
    # Get saved projects for the current user
    saved_projects = ProjectMollier.objects.filter(user=request.user).order_by('-created_at')
   
    # Check if we are restoring a session project
    restored_sessionstorage = request.session.pop('restored_sessionstorage', None)
    comfort_stats = mollierView_output[7] or {}
    comfort_polygons = mollierView_output[8] or {}
    comfort_zone_values = {
        'temp_min': request.POST.get('comfort_temp_min') or '20',
        'temp_max': request.POST.get('comfort_temp_max') or '24',
        'rh_min': request.POST.get('comfort_rh_min') or '30',
        'rh_max': request.POST.get('comfort_rh_max') or '70',
    }
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
        'climate_heatmap': json.dumps(mollierView_output[6]),  # Used for heatmap climateyearNEN5060
        'comfort_stats_json': json.dumps(comfort_stats),  # Used for comfort stats
        'comfort_stats': comfort_stats, 
        'comfort_polygons': json.dumps(comfort_polygons),
        'comfort_zone_polygon': json.dumps(mollierView_output[9]),
        'comfort_zone_values': comfort_zone_values,
        'process_steps': list(range(1, 5)),  # Used for template iteration
        'username': [request.user.first_name, request.user.last_name,request.user.username],
        'saved_projects': saved_projects,  # Pass projects to template
        'restored_sessionstorage': json.dumps(restored_sessionstorage) if restored_sessionstorage else None
    })
    

# expansievat pagina
@login_required(login_url='accounts:login')
def tool_W2(request):
    volume_input_error = None
    system_volume_unknown = request.method == 'POST' and request.POST.get(
        'sys_inhoud_onbekend'
    ) == 'on'
    if system_volume_unknown:
        try:
            entered_power = float(request.POST.get('vermogen', ''))
        except ValueError:
            entered_power = 0
        if not math.isfinite(entered_power) or entered_power <= 0:
            expansievat_ouput = []
            volume_input_error = (
                'Vul het vermogen van de cv-ketel in om de systeeminhoud te schatten.'
            )
        else:
            expansievat_ouput = expansievat(request)
    else:
        expansievat_ouput = expansievat(request)
    pressure_diagram = None
    if expansievat_ouput:
        pressure_diagram = build_pressure_height_diagram(
            expansievat_ouput[14],
            expansievat_ouput[4],
            expansievat_ouput[11],
        )
    return render(request, 'tools/tool_W2.html', {
        'expansievat_output': expansievat_ouput,
        'pressure_diagram': pressure_diagram,
        'volume_input_error': volume_input_error,
        'system_volume_unknown': system_volume_unknown,
    })

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

#------------------------------------------------------------------------------------------------------------------------------
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
def generate_pdf_W1(request):
    return generate_pdf_mollier(request)
def generate_pdf_W4(request):
    return generate_pdf_CO2(request)
@login_required(login_url='accounts:login')
def generate_pdf_A3(request):
    return generate_pdf_climate(request)

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


@login_required(login_url='accounts:login')
def sfb_search(request):
    query = request.GET.get("q", "").strip()

    if len(query) < 2:
        return JsonResponse({
            "query": query,
            "routes": {}
        })

    # ✅ Nieuwe logica: automatische inschatting
    routes = analyse_search_term(query)

    return JsonResponse({
        "query": query,
        "routes": routes,
    })


@login_required(login_url='accounts:login')



def nlsfb_children_view(request, code):
    children = get_children(code)

    data = [
        {"code": c.code, "omschrijving": c.omschrijving}
        for c in children
    ]
    return JsonResponse(data, safe=False)
