from django.urls import path
from .views import AgenteList, crear_Incidencias_Transito, nuevo_usuario, nuevo_usuariojuez, nuevo_usuarioadmin, agenteoperativo, anadirfoto
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('agente/', login_required(AgenteList.as_view()), name='agente_list'),
    # path('api-token-auth/',views.obtain_auth_token,name='api-token-auth')
    path('incidencias/', login_required(crear_Incidencias_Transito), name='incidencias'),
    path('usuarionuevo/',login_required(nuevo_usuario.as_view()), name='usuarionuevo'),
    path('usuarionuevojuez/',login_required(nuevo_usuariojuez.as_view()), name='usuarionuevojuez'),
    path('usuarionuevoadmin/',login_required(nuevo_usuarioadmin.as_view()), name='usuarionuevoadmin'),
    path('agenteoperativo/',login_required(agenteoperativo), name='agenteoperativo'),
    path('anadirfoto/', login_required(anadirfoto), name='anadirfoto'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
