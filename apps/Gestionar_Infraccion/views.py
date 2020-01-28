from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from .forms import Articulos_COIPForm, Infraccion_TransitoForm, IntentosForm, ContadorInfForm
from apps.Gestionar_Informacion.forms import ConductorForm, VehiculoForm
from apps.Gestionar_Evidencia.forms import imageform, videoform, audioform
from .models import Infraccion_Transito, Articulos_COIP, Intentos, ContadorInfraccion
from django.views.generic import View, TemplateView, ListView, UpdateView, CreateView, DeleteView
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import ArticulosSerializer, InfraccionSerializer
from apps.Gestionar_Informacion.models import Conductor, Vehiculo
from apps.Gestionar_Evidencia.models import MyImage, MyVideo, MyAudio
from apps.Gestionar_Usuarios.models import Agente_Transito
from apps.Gestionar_Accidente.models import Accidente_Transito
from apps.Gestionar_Usuarios.forms import Agente_Transito_Form

from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
import datetime



from django.http import HttpResponse
from .utils import render_to_pdf #created in step 4
from django.template.loader import get_template

class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        id = request.GET['Infraccion_Transito']
        infraccion = Infraccion_Transito.objects.all().filter(NumeroInfraccion=id)
        data = {'hour': datetime.datetime.now(), 'infraccion' : infraccion}
        pdf = render_to_pdf('Gestionar_Infraccion/invoice.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


class ArticulosList(generics.ListCreateAPIView):
    queryset = Articulos_COIP.objects.all()
    serializer_class = ArticulosSerializer
    permission_classes = (IsAuthenticated,)
    authentication_class = (TokenAuthentication,)


class InfraccionList(generics.ListCreateAPIView):
    queryset = Infraccion_Transito.objects.all()
    serializer_class = InfraccionSerializer
    permission_classes = (IsAuthenticated,)
    authentication_class = (TokenAuthentication,)


def home(request):
    infracciones = Infraccion_Transito.objects.all()
    accidentes = Accidente_Transito.objects.all()

    fechaInicio = request.POST.get('FechaInicio')
    fechaFin = request.POST.get('FechaFin')

    if request.method == 'POST':
        if (str(fechaFin)+'' != '') & (str(fechaInicio)+'' != ''):
            try:
                accidentes = Accidente_Transito.objects.filter(
                    Fecha__gte=fechaInicio, Fecha__lte=fechaFin)

                infracciones = Infraccion_Transito.objects.all().filter(
                    Fecha_Infraccion__gte=fechaInicio, Fecha_Infraccion__lte=fechaFin)

                return render(request, 'index.html', {'infracciones': infracciones, 'accidentes': accidentes})

            except Accidente_Transito.DoesNotExist:
                return render(request, 'index.html', {'infracciones': infracciones, 'accidentes': accidentes})

        else:
            return render(request, 'index.html', {'infracciones': infracciones, 'accidentes': accidentes})

    else:

        for inf in Infraccion_Transito.objects.all().filter(Estado='Reportado'):
            ac = datetime.date.today()
            s = str(inf.Fecha_Registro)
          
            dates = datetime.datetime.strptime(s, '%Y-%m-%d').date()
            modified_date = dates + datetime.timedelta(days=3)

            if ac >= modified_date:
                inf.Estado = 'Pendiente de pago'
                inf.save()
        return render(request, 'index.html', {'infracciones': infracciones, 'accidentes': accidentes})


def homejuez(request):
    return render(request, 'indexjuez.html')


def redireccionar(request):
    return render(request, 'redireccionar.html')



def crearArticulos_COIP(request):
    if request.method == 'POST':
        print(request.POST)
        articulos_coip_form = Articulos_COIPForm(request.POST)
        if articulos_coip_form.is_valid():
            articulos_coip_form.save()
            messages.warning(request, 'Registro Correcto')
            return redirect('index')
        else:
            messages.warning(request, 'Error en el formulario')
            return render(request, 'Gestionar_Infraccion/crear_articulos_coip.html', {'articulos_coip_form': articulos_coip_form})
    else:
        articulos_coip_form = Articulos_COIPForm()
        return render(request, 'Gestionar_Infraccion/crear_articulos_coip.html', {'articulos_coip_form': articulos_coip_form})


def crearInfraccion_Transito(request):
    if request.method == 'POST':
        infraccion_transito_form = Infraccion_TransitoForm(request.POST)
        articulos_coip_form = Articulos_COIPForm(request.POST)
        conductorform = ConductorForm(request.POST)
        vehiculoform = VehiculoForm(request.POST)
        audform = audioform(request.POST, request.FILES) 
        vidform = videoform(request.POST, request.FILES)
        fotoform = imageform(request.POST, request.FILES)
        agenteform = Agente_Transito_Form(request.POST)
        contadorform =ContadorInfForm(request.POST)


        if infraccion_transito_form.is_valid() & articulos_coip_form.is_valid():

            agente = Agente_Transito.objects.get(Cedula=request.POST.get('Cedula'))

            contador = ContadorInfraccion()
            contador.CedulaAgente = request.POST.get('Cedula') 
            contador.CodigoAgente = agente.Codigo_Agente
            contador.ContadorAgente = request.POST.get('ContadorInf')
            contador.save()

            agt =Agente_Transito()
            agt.Cedula = request.POST.get('Cedula')
            agt.Nombres = request.POST.get('Nombres')
            agt.Apellidos = request.POST.get('Apellidos')

            articulo = Articulos_COIP()
            articulo.Id_Articulo = request.POST.get('NumeroInfraccion')
            articulo.Articulo = request.POST.get('Articulo')
            articulo.Inciso = request.POST.get('Inciso')
            articulo.Numeral = request.POST.get('Numeral')
            articulo.save()

            cd = Conductor()
            cd.CedulaC = request.POST.get('CedulaC')
            cd.Nombres = request.POST.get('Nombres')
            cd.Apellidos = request.POST.get('Apellidos')
            cd.TipoLicencia = request.POST.get('TipoLicencia')
            cd.CategoriaLicencia = request.POST.get('CategoriaLicencia')
            cd.FechaEmisionLicencia= request.POST.get('FechaEmisionLicencia')
            cd.FechaCaducidadLicencia = request.POST.get('FechaCaducidadLicencia')

            vehiculo = Vehiculo()
            vehiculo.Placa = request.POST.get('Placa')
            vehiculo.Marca = request.POST.get('Marca')
            vehiculo.Tipo = request.POST.get('Tipo')
            vehiculo.Color = request.POST.get('Color')
            vehiculo.FechaMatricula = request.POST.get('FechaMatricula')
            vehiculo.FechaCaducidadMatricula = request.POST.get('FechaCaducidadMatricula')

            infraccionT = Infraccion_Transito()
            infraccionT.NumeroInfraccion = request.POST.get('NumeroInfraccion')
            infraccionT.Descripcion = request.POST.get('Descripcion')
            infraccionT.Ubicacion = request.POST.get('Ubicacion')
            infraccionT.Latitud = request.POST.get('Latitud')
            infraccionT.Longitud = request.POST.get('Longitud')
            infraccionT.Estado = request.POST.get('Estado')
            infraccionT.Fecha_Infraccion = request.POST.get('Fecha_Infraccion')
            infraccionT.Hora_Infraccion = request.POST.get('Hora_Infraccion')
            infraccionT.Hora_Detencion = request.POST.get('Hora_Detencion')
            infraccionT.Agente = agt
            infraccionT.ArticuloC = articulo
            infraccionT.Conductor = cd
            infraccionT.Vehiculo = vehiculo
            infraccionT.save()

            foto = MyImage()
            foto.model_pic = request.POST.get('model_pic')
            foto.id_Evidencia = request.POST.get('NumeroInfraccion')
            if foto.model_pic != '':
                foto.model_pic = request.FILES.get('model_pic')
                foto.save()

            audio = MyAudio()
            audio.model_aud = request.POST.get('model_aud')
            audio.id_Evidencia = request.POST.get('NumeroInfraccion')
            if audio.model_aud != '':
                audio.model_aud = request.FILES.get('model_aud')
                audio.save()

            video = MyVideo()
            video.model_vid = request.POST.get('model_vid')
            video.id_Evidencia = request.POST.get('NumeroInfraccion')
            if video.model_vid != '':
                video.model_vid = request.FILES.get('model_vid')
                video.save()
            
            messages.warning(request, 'Registro Correcto')
            return redirect('index')  # retorno de confirmacion
        else:
            messages.warning(request, 'Error en el formulario')
            return render(request,'Gestionar_Infraccion/crear_infraccion_transito.html',{'infraccion_transito_form':infraccion_transito_form, 'articulos_coip_form':articulos_coip_form, 'conductorform':conductorform, 'vehiculoform':vehiculoform, 'audform': audform, 'vidform': vidform, 'fotoform': fotoform, 'contadorform':contadorform, 'agenteform': agenteform})
    else:
        infraccion_transito_form = Infraccion_TransitoForm()
        articulos_coip_form = Articulos_COIPForm()
        conductorform = ConductorForm()
        vehiculoform = VehiculoForm()
        agenteform = Agente_Transito_Form()
        audform = audioform(request.POST, request.FILES) 
        vidform = videoform(request.POST, request.FILES)
        fotoform = imageform(request.POST, request.FILES)
        contadorform =ContadorInfForm()
        messages.warning(request, 'Error')
        return render(request, 'Gestionar_Infraccion/crear_infraccion_transito.html', {'infraccion_transito_form': infraccion_transito_form, 'articulos_coip_form': articulos_coip_form, 'conductorform': conductorform, 'vehiculoform': vehiculoform, 'agenteform': agenteform, 'audform': audform, 'vidform': vidform, 'fotoform': fotoform})


def buscar_InfraccionNumAgente(request):
    if request.method == 'POST':
        codAgente = request.POST.get('Codigo_Agente')
        try:
            agente = Agente_Transito.objects.get(Codigo_Agente=codAgente)
        except Exception as e:
            raise e


def listarInfraccion(request):
    infracciones = Infraccion_Transito.objects.all()
    NumeroInfraccion = 0  # filtro por defecto
    if request.POST.get('NumeroInfraccion'):
        NumeroInfraccion = int(request.POST.get('NumeroInfraccion'))
        infracciones = infracciones.filter(
            NumeroInfraccion__gte=NumeroInfraccion)
    return render(request, 'Gestionar_Infraccion/listar_infraccion_transito.html', {'infracciones': infracciones, 'NumeroInfraccion': NumeroInfraccion})


def buscar_intentos(request):
    intentos = Intentos.objects.filter(Accion=0)
    Cedula = ''  # filtro por defecto
    intentoform = IntentosForm()
    intentoform = IntentosForm(request.POST)
    if request.POST.get('Cedula'):
        Cedula = int(request.POST.get('Cedula'))
        intentos = intentos.filter(Cedula=Cedula)
    return render(request, 'Gestionar_Infraccion/consultaIntentos.html', {'intentos': intentos, 'Cedula': Cedula, 'intentoform': intentoform})



def buscar_infracciones(request):
    if request.method == 'POST':
        numeroInfraccion = request.POST.get('NumeroInfraccion')
        fechaInicio = request.POST.get('FechaInicio')
        fechaFin = request.POST.get('FechaFin')
        conductor = request.POST.get('Conductor')
        vehiculo = request.POST.get('Vehiculo')
        estado = request.POST.get('Estado')

        if (str(numeroInfraccion) != '') & ((str(fechaInicio) == '') | (str(fechaFin) == '')):
            try:
                infraccion = Infraccion_Transito.objects.all().filter(
                    NumeroInfraccion=numeroInfraccion)
                context = {
                    'infraccion': infraccion,
                }
                return render(request, 'Gestionar_Infraccion/consultaInfraccion.html', context)
            except Exception as e:
                messages.warning(request, "No encontrado")
                return render(request, 'Gestionar_Infraccion/consultaInfraccion.html')
        elif (str(fechaInicio) != '') & (str(fechaFin) != ''):
            try:

                infraccion = Infraccion_Transito.objects.all().filter(
                    Fecha_Infraccion__gte=fechaInicio, Fecha_Infraccion__lte=fechaFin)
                print(infraccion)
                context = {
                    'infraccion': infraccion,
                }
                return render(request, 'Gestionar_Infraccion/consultaInfraccion.html', context)
            except Exception as e:
                messages.warning(request, "No encontrado")
                return render(request, 'Gestionar_Infraccion/consultaInfraccion.html')

        elif (str(conductor) != ''):
            try:
                infraccion = Infraccion_Transito.objects.all().filter(Conductor=conductor)
                context = {
                    'infraccion': infraccion,
                }
                return render(request, 'Gestionar_Infraccion/consultaInfraccion.html', context)
            except Exception as e:
                messages.warning(request, "No encontrado")
                return render(request, 'Gestionar_Infraccion/consultaInfraccion.html')

        elif (str(estado) != ''):
            try:
                infraccion = Infraccion_Transito.objects.all().filter(Estado=estado)
                context = {
                    'infraccion': infraccion,
                }
                return render(request, 'Gestionar_Infraccion/consultaInfraccion.html', context)
            except Exception as e:
                messages.warning(request, "No encontrado")
                return render(request, 'Gestionar_Infraccion/consultaInfraccion.html')

        elif (str(vehiculo) != ''):
            try:
                infraccion = Infraccion_Transito.objects.all().filter(Vehiculo=vehiculo)
                context = {
                    'infraccion': infraccion,
                }
                return render(request, 'Gestionar_Infraccion/consultaInfraccion.html', context)
            except Exception as e:
                messages.warning(request, "No encontrado")
                return render(request, 'Gestionar_Infraccion/consultaInfraccion.html')

        else:
            messages.warning(request, "Ingrese numero")
            return render(request, 'Gestionar_Infraccion/consultaInfraccion.html')
    else:
        return render(request, 'Gestionar_Infraccion/consultaInfraccion.html')


def buscar_infracciones_juez(request):
    if request.method == 'POST':
        numeroInfraccion = request.POST.get('NumeroInfraccion')
        conductor = request.POST.get('Conductor')
        vehiculo = request.POST.get('Vehiculo')

        if (str(numeroInfraccion) != ''):
            try:
                infraccion = Infraccion_Transito.objects.all().filter(
                    NumeroInfraccion=numeroInfraccion)
                context = {
                    'infraccion': infraccion,
                }
                return render(request, 'Gestionar_Infraccion/consultaInfraccionjuez.html', context)
            except Exception as e:
                messages.warning(request, "No encontrado")
                return render(request, 'Gestionar_Infraccion/consultaInfraccionjuez.html')
        elif (str(conductor) != ''):
            try:
                infraccion = Infraccion_Transito.objects.all().filter(Conductor=conductor)
                context = {
                    'infraccion': infraccion,
                }
                return render(request, 'Gestionar_Infraccion/consultaInfraccionjuez.html', context)
            except Exception as e:
                messages.warning(request, "No encontrado")
                return render(request, 'Gestionar_Infraccion/consultaInfraccionjuez.html')

        elif (str(vehiculo) != ''):
            try:
                infraccion = Infraccion_Transito.objects.all().filter(Vehiculo=vehiculo)
                context = {
                    'infraccion': infraccion,
                }
                return render(request, 'Gestionar_Infraccion/consultaInfraccionjuez.html', context)
            except Exception as e:
                messages.warning(request, "No encontrado")
                return render(request, 'Gestionar_Infraccion/consultaInfraccionjuez.html')

        else:
            messages.warning(request, "Ingrese numero")
            return render(request, 'Gestionar_Infraccion/consultaInfraccionjuez.html')
    else:
        return render(request, 'Gestionar_Infraccion/consultaInfraccionjuez.html')


def listarIntento(request):
    if request.method == 'GET':
        id = request.GET['Intentos']
        intentos = Intentos.objects.all().filter(Cedula=id, Accion=1)

    context = {'intentos': intentos,
               }
    return render(request, 'Gestionar_Infraccion/intentoControl.html', context)


def mapaIntento(request):
    if request.method == 'POST':
        id = request.GET['Intentos']
        intentos1 = Intentos.objects.get(id=id)
        intentos1.Descripcion = request.POST.get('Descripcion') 
        intentos1.Accion=1
        intentos1.save()
        messages.warning(request, 'Actualizacion correcta')
        return redirect('/Gestionar_Infraccion/buscar_Intentos/')
    else:
        intentoform = IntentosForm()
        id = request.GET['Intentos']
        intentos = Intentos.objects.all().filter(id=id)

        context = {'intentos': intentos,'intentoform': intentoform,}

        return render(request, 'Gestionar_Infraccion/mapaintento.html', context)

def mapaIntentoaccion(request):
    intentoform = IntentosForm()
    id = request.GET['Intentos']
    intentos = Intentos.objects.all().filter(id=id)
    context = {'intentos': intentos,'intentoform': intentoform,}
    return render(request, 'Gestionar_Infraccion/mapaintentoaccion.html', context)


def mapaInfraccion(request):
    if request.method == 'GET':
        id = request.GET['Infraccion_Transito']
        infraccion = Infraccion_Transito.objects.all().filter(NumeroInfraccion=id)

    context = {'infraccion': infraccion,
               }
    return render(request, 'Gestionar_Infraccion/mapaInfraccion.html', context)


def Reportesadicionar(request):
    if request.method == 'POST':
        audform = audioform(request.POST, request.FILES) 
        vidform = videoform(request.POST, request.FILES)
        fotoform = imageform(request.POST, request.FILES)
        id = request.GET['Infraccion_Transito']
        infraccion1 = Infraccion_Transito.objects.get(NumeroInfraccion=id)
        


        if infraccion1.Estado == 'Impugnada':
            infraccion_form = Infraccion_TransitoForm()
            audform = audioform(request.POST, request.FILES) 
            vidform = videoform(request.POST, request.FILES)
            fotoform = imageform(request.POST, request.FILES)
            id = request.GET['Infraccion_Transito']
            infraccion = Infraccion_Transito.objects.all().filter(NumeroInfraccion=id)
            context = {'infraccion': infraccion, 'infraccion_form': infraccion_form, 'audform': audform, 'vidform': vidform, 'fotoform': fotoform}
            messages.warning(request, 'No se puede modificar este estado')
            return render(request, 'Gestionar_Infraccion/reportes.html', context)

        if infraccion1.Estado == 'No impugnada':
            messages.warning(request, 'No se puede modificar este estado')
            return render(request, 'Gestionar_Infraccion/reportes.html')

        if infraccion1.Estado == 'Pendiente de pago':
            messages.warning(request, 'No se puede modificar este estado')
            return render(request, 'Gestionar_Infraccion/reportes.html')

        if infraccion1.Estado == 'Pagada':
            messages.warning(request, 'No se puede modificar este estado')
            return render(request, 'Gestionar_Infraccion/reportes.html')
        

        infraccion1.Estado = request.POST.get('Estado')


        if infraccion1.Estado == 'No impugnada':
            infraccion1.Estado = 'Pendiente de pago'
        infraccion1.save()


        foto = MyImage()
        foto.model_pic = request.POST.get('model_pic')
        foto.id_Evidencia = request.GET['Infraccion_Transito']
        if foto.model_pic != '':
            foto.model_pic = request.FILES.get('model_pic')
            foto.save()

        audio = MyAudio()
        audio.model_aud = request.POST.get('model_aud')
        audio.id_Evidencia = request.GET['Infraccion_Transito']
        if audio.model_aud != '':
            audio.model_aud = request.FILES.get('model_aud')
            audio.save()

        video = MyVideo()
        video.model_vid = request.POST.get('model_vid')
        video.id_Evidencia = request.GET['Infraccion_Transito']
        if video.model_vid != '':
            video.model_vid = request.FILES.get('model_vid')
            video.save()

        messages.warning(request, 'Actualizacion correcta')
        return redirect('/Gestionar_Infraccion/consultar_Infraccion/')
    else:
        infraccion_form = Infraccion_TransitoForm()
        audform = audioform(request.POST, request.FILES) 
        vidform = videoform(request.POST, request.FILES)
        fotoform = imageform(request.POST, request.FILES)
        id = request.GET['Infraccion_Transito']
        infraccion = Infraccion_Transito.objects.all().filter(NumeroInfraccion=id)
        context = {'infraccion': infraccion, 'infraccion_form': infraccion_form, 'audform': audform, 'vidform': vidform, 'fotoform': fotoform}
        return render(request, 'Gestionar_Infraccion/reportes.html', context)


def Intento_Transito(request):
    if request.method == 'POST':
        id = request.GET('Intentos')
        try:
            intento = Intentos.objects.all.filter(
                id=id)
            intento.Descripcion = request.POST.get('Descripcion')
            intento.Accion = 1
            intento.save()
            messages.warning(request, 'Actualizacion correcta')
            return redirect('/Gestionar_Infraccion/buscar_Intentos/')

        except Exception as e:
            accidente_transitoForm = Accidente_TransitoForm()
            messages.warning(request, 'Numero Incorrecto')
            return redirect('/Gestionar_Infraccion/buscar_Intentos/')
