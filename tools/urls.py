from . import views
from django.urls import path

app_name = 'tools'

urlpatterns = [
    path('', views.tools, name='tools'),
    path('gebouwgegevens', views.tool_A1),
    path('omrekenfactoren/druk', views.tool_A2_1),
    path('omrekenfactoren/volume', views.tool_A2_2),
    path('omrekenfactoren/debiet', views.tool_A2_3),
    path('omrekenfactoren/massa', views.tool_A2_4),
    path('omrekenfactoren/energie', views.tool_A2_5),   
    path('buffervat', views.tool_W1),
]