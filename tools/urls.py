from . import views
from django.urls import path


app_name = 'tools'

urlpatterns = [
    path('', views.tools, name='tools'),
    path('gebouwgegevens', views.tool_A1, name='gebouwgegevens'),
    path('eenhedenconversie', views.tool_A2, name='eenhedenconversie'),
    path('klimaatjaar', views.tool_A3, name='klimaatjaar'),
    path('mollierdiagram', views.tool_W1, name ='mollier'),
    path('expansievat', views.tool_W2, name='expansievat'),
    path('drukverlies', views.tool_W3, name='drukverlies'),
    path('download-excel/', views.download_excel, name='download_excel'),
]