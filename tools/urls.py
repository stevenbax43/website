from . import views
from django.urls import path


app_name = 'tools'

urlpatterns = [
    path('', views.tools, name='tools'),
    path('gebouwgegevens', views.tool_A1, name='gebouwgegevens'),
    path('eenhedenconversie', views.tool_A2, name='eenhedenconversie'),
    path('klimaatjaar', views.tool_A3, name='klimaatjaar'),
    path('mollierdiagram', views.tool_W1, name ='mollier'),
    path('save-project/', views.save_project, name='save_project'),
    path('load-project/', views.load_project, name='load_project'),
    path('generate-pdf/', views.generate_pdf, name='generate_pdf'),
    path('delete-project/', views.delete_project, name='delete_project'),
    path('expansievat', views.tool_W2, name='expansievat'),
    path('leidingverliezen', views.tool_W3, name='drukverlies'),
    path('CO2verloop', views.tool_W4, name='CO2verloop'),
    path('buffervat', views.tool_W5, name='buffervat'),
    path('thermisch-vermogen', views.tool_W6, name='thermisch_vermogen'),
    path('driefase-vermogen', views.tool_E1, name='driefase_vermogen'),
    path('download-excel/', views.download_excel, name='download_excel'),
    path("readme/<slug:tool>/", views.tool_readme, name="tool-readme"),
]