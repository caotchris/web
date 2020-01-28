from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from .views import crearAccidente_Transito, AccidenteList, buscarAccidente_Transito, detalleAccidente_Transito, mapaAccidente, crearAccidente_Transito_juez, Reportesadicionara

urlpatterns = [
    path('crear_accidente_transito/', login_required(crearAccidente_Transito),
         name='crear_accidente_transito'),
    path('crear_accidente_transito_juez/', login_required(crearAccidente_Transito_juez),
         name='crear_accidente_transito_juez'),
    path('accidente/', AccidenteList.as_view(), name='accidente_list'),
    path('bucar_accidente_transito/', login_required(buscarAccidente_Transito),
         name='buscar_accidente_transito'),
    path('detalle_accidente_transito/', login_required(detalleAccidente_Transito),
         name='detalle_accidente_transito'),
    path('mapaAccidente/', login_required(mapaAccidente)),
    path('Reportesadicionara/', login_required(Reportesadicionara)),

]
