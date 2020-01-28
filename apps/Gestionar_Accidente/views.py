from django.shortcuts import render, redirect
from .forms import Accidente_TransitoForm
from apps.Gestionar_Evidencia.forms import imageform, videoform, audioform
from .models import Accidente_Transito
from apps.Gestionar_Evidencia.models import MyImage, MyVideo, MyAudio
from rest_framework import generics
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView
from django.contrib.auth.forms import AuthenticationForm
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import AccidenteSerializer
from django.contrib import messages


class AccidenteList(generics.ListCreateAPIView):
    queryset = Accidente_Transito.objects.all()
    serializer_class = AccidenteSerializer
    permission_classes = (IsAuthenticated,)
    authentication_class = (TokenAuthentication,)


def crearAccidente_Transito(request):

    NumeroAccidente = request.POST.get('NumeroAccidente')
    TipoAccidente = request.POST.get('TipoAccidente')
    fechaInicio = request.POST.get('FechaInicio')
    fechaFin = request.POST.get('FechaFin')

    if str(NumeroAccidente)+'' != '':
        try:
            print("!!!!1")
            accidentes = Accidente_Transito.objects.filter(pk=NumeroAccidente)

            return render(request, 'Gestionar_Accidente/crear_accidente_transito.html', {'accidentes': accidentes})
        except Accidente_Transito.DoesNotExist:
            messages.warning(request, 'No se encontraron coincidencias')
            return render(request, 'Gestionar_Accidente/crear_accidente_transito.html')
    elif str(TipoAccidente)+'' != '':
        try:
            print("!!!!2")
            accidentes = Accidente_Transito.objects.filter(
                TipoAccidente=TipoAccidente)

            return render(request, 'Gestionar_Accidente/crear_accidente_transito.html', {'accidentes': accidentes})
        except Accidente_Transito.DoesNotExist:
            messages.warning(request, 'No se encontraron coincidencias')
            return render(request, 'Gestionar_Accidente/crear_accidente_transito.html')
    elif (str(fechaFin)+'' != '') & (str(fechaInicio)+'' != ''):
        try:
            print("!!!!3")
            accidentes = Accidente_Transito.objects.filter(
                Fecha__gte=fechaInicio, Fecha__lte=fechaFin)
            return render(request, 'Gestionar_Accidente/crear_accidente_transito.html', {'accidentes': accidentes})
        except Accidente_Transito.DoesNotExist:
            messages.warning(request, 'No se encontraron coincidencias')
            return render(request, 'Gestionar_Accidente/crear_accidente_transito.html')

    else:
        messages.warning(request, 'Ingrese NumeroAccidente')
        return render(request, 'Gestionar_Accidente/crear_accidente_transito.html')


def crearAccidente_Transito_juez(request):

    NumeroAccidente = request.POST.get('NumeroAccidente')
    TipoAccidente = request.POST.get('TipoAccidente')
    fechaInicio = request.POST.get('FechaInicio')
    fechaFin = request.POST.get('FechaFin')

    if str(NumeroAccidente)+'' != '':
        try:
            print("!!!!1")
            accidentes = Accidente_Transito.objects.filter(pk=NumeroAccidente)

            return render(request, 'Gestionar_Accidente/crear_accidente_transito_juez.html', {'accidentes': accidentes})
        except Accidente_Transito.DoesNotExist:
            messages.warning(request, 'No se encontraron coincidencias')
            return render(request, 'Gestionar_Accidente/crear_accidente_transito_juez.html')
    elif str(TipoAccidente)+'' != '':
        try:
            print("!!!!2")
            accidentes = Accidente_Transito.objects.filter(
                TipoAccidente=TipoAccidente)

            return render(request, 'Gestionar_Accidente/crear_accidente_transito_juez.html', {'accidentes': accidentes})
        except Accidente_Transito.DoesNotExist:
            messages.warning(request, 'No se encontraron coincidencias')
            return render(request, 'Gestionar_Accidente/crear_accidente_transito_juez.html')
    elif (str(fechaFin)+'' != '') & (str(fechaInicio)+'' != ''):
        try:
            print("!!!!3")
            accidentes = Accidente_Transito.objects.filter(
                Fecha__gte=fechaInicio, Fecha__lte=fechaFin)
            return render(request, 'Gestionar_Accidente/crear_accidente_transito_juez.html', {'accidentes': accidentes})
        except Accidente_Transito.DoesNotExist:
            messages.warning(request, 'No se encontraron coincidencias')
            return render(request, 'Gestionar_Accidente/crear_accidente_transito_juez.html')

    else:
        messages.warning(request, 'Ingrese NumeroAccidente')
        return render(request, 'Gestionar_Accidente/crear_accidente_transito_juez.html')


def buscarAccidente_Transito(request):
    if request.method == 'POST':
        try:
            numeroAccidente = request.POST.get('NumeroAccidente')
            # accidente = Accidente_Transito.objects.all().filter(
            #     NumeroAccidente=request.POST.get('NumeroAccidente'))
            return redirect("/Gestionar_Accidente/detalle_accidente_transito/?NumeroAccidente="+numeroAccidente)
        except Exception as e:
            accidente_transitoForm = Accidente_TransitoForm()
            messages.warning(request, 'Ingrese NumeroAccidente')
            return render(request, 'Gestionar_Accidente/buscar_accidente.html', {'accidente_transitoForm': accidente_transitoForm})

    else:
        accidente_transitoForm = Accidente_TransitoForm()
        return render(request, 'Gestionar_Accidente/buscar_accidente.html', {'accidente_transitoForm': accidente_transitoForm})


def detalleAccidente_Transito(request):
    if request.method == 'POST':
        numeroAccidente = request.POST.get('NumeroAccidente')
        try:
            accidente = Accidente_Transito.objects.get(
                NumeroAccidente=numeroAccidente)
            accidente.Estado = request.POST.get('Estado')
            accidente.save()
            messages.warning(request, 'Actualizacion correcta')
            return redirect('/Gestionar_Accidente/bucar_accidente_transito/')

        except Exception as e:
            accidente_transitoForm = Accidente_TransitoForm()
            messages.warning(request, 'Numero Incorrecto')
            return redirect('/Gestionar_Accidente/bucar_accidente_transito/')

    else:
        try:
            accidente = Accidente_Transito.objects.all().filter(
                NumeroAccidente=request.GET['NumeroAccidente'])
            accidente_transitoForm = Accidente_TransitoForm()
            contex = {
                'accidente': accidente,
                'accidente_transitoForm': accidente_transitoForm
            }
            return render(request, 'Gestionar_Accidente/formulario_accidente.html', contex)
        except Exception as e:
            messages.warning(request, 'Numero Incorrecto')
            accidente_transitoForm = Accidente_TransitoForm()
            return redirect('/Gestionar_Accidente/bucar_accidente_transito/')


def mapaAccidente(request):
    if request.method == 'GET':
        id = request.GET['Accidente_Transito']
        accidente = Accidente_Transito.objects.all().filter(NumeroAccidente=id)

    context = {'accidente': accidente,
               }
    return render(request, 'Gestionar_Accidente/mapaAccidente.html', context)


def Reportesadicionara(request):
    if request.method == 'POST':
        id = request.GET['Accidente_Transito']
        accidente1 = Accidente_Transito.objects.get(NumeroAccidente=id)
        accidente1.Estado = request.POST.get('Estado')
        accidente1.save()

        foto = MyImage()
        foto.model_pic = request.POST.get('model_pic')
        foto.id_Evidencia = request.GET['Accidente_Transito']
        if foto.model_pic != '':
            foto.save()

        audio = MyAudio()
        audio.model_aud = request.POST.get('model_aud')
        audio.id_Evidencia = request.GET['Accidente_Transito']
        if audio.model_aud != '':
            audio.save()

        video = MyVideo()
        video.model_vid = request.POST.get('model_vid')
        video.id_Evidencia = request.GET['Accidente_Transito']
        if video.model_vid != '':
            video.save()

        messages.warning(request, 'Actualizacion correcta')
        return redirect('/Gestionar_Accidente/crear_accidente_transito/')
    else:
        accidente_form = Accidente_TransitoForm()
        audform = audioform(request.POST)
        vidform = videoform(request.POST)
        fotoform = imageform(request.POST)
        id = request.GET['Accidente_Transito']
        accidente = Accidente_Transito.objects.all().filter(NumeroAccidente=id)
        context = {'accidente': accidente, 'accidente_form': accidente_form,
                   'audform': audform, 'vidform': vidform, 'fotoform': fotoform}
        return render(request, 'Gestionar_Accidente/reportesa.html', context)
