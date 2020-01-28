from django.shortcuts import render, redirect
from rest_framework import generics
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import CreateView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .forms import Agente_Transito_Form, RegistroForm
from .models import Agente_Transito
from apps.Gestionar_Accidente.models import Accidente_Transito
from apps.Gestionar_Infraccion.models import Infraccion_Transito
from .serializers import AgenteSerializer, userSerializer
from django.contrib.auth.models import User
from django.contrib import auth

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import Group



class AgenteList(generics.ListCreateAPIView):
    queryset = Agente_Transito.objects.all()
    serializer_class = AgenteSerializer
    permission_classes = (IsAuthenticated,)
    authentication_class = (TokenAuthentication,)

class Login(FormView):
    template_name = "login.html"
    form_class = AuthenticationForm
    success_url = reverse_lazy('redireccionar')


    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(Login, self).dispatch(request, *args, *kwargs)

    def form_valid(self, form):

        user = authenticate(
            username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        token, _ = Token.objects.get_or_create(user=user)
        if token:
            login(self.request, form.get_user())
            return super(Login, self).form_valid(form)

def Logout(request):
    auth.logout(request)
    return redirect('/')


def crear_Incidencias_Transito(request):
    accidente = Accidente_Transito.objects.all()
    Cedula = ''  # filtro por defecto
    if request.POST.get('incidencias'):
        Cedula = int(request.POST.get('incidencias'))
        intentos = intentos.filter(Cedula=Cedula)
    return render(request, 'Gestionar_Infraccion/consultaIntentos.html', {'intentos': intentos, 'Cedula': Cedula})


def homeadmin(request):
    return render(request, 'indexadmin.html')


class nuevo_usuario(CreateView):
    model = User
    template_name = "nuevousuario.html"
    form_class = RegistroForm
    success_url = reverse_lazy('indexadmin')

    def form_valid(self,form):
        group=Group.objects.get(name='Agenteadmin')
        self.object = form.save(commit=False)
        self.object.save()
        
        return HttpResponseRedirect(self.get_success_url())

class nuevo_usuariojuez(CreateView):
    model = User
    template_name = "Gestionar_Usuarios/nuevousuariojuez.html"
    form_class = RegistroForm
    success_url = reverse_lazy('indexadmin')

    def form_valid(self,form):
        group=Group.objects.get(name='Juez')
        self.object = form.save(commit=False)
        self.object.save()
        
        return HttpResponseRedirect(self.get_success_url())

class nuevo_usuarioadmin(CreateView):
    model = User
    template_name = "Gestionar_Usuarios/nuevousuarioadmin.html"
    form_class = RegistroForm
    success_url = reverse_lazy('indexadmin')

    def form_valid(self,form):
        group=Group.objects.get(name='Administrador')
        self.object = form.save(commit=False)
        self.object.save()
        messages.warning(request, "Usuario agregado correctamente")
        return HttpResponseRedirect(self.get_success_url())


def agenteoperativo(request):
   if request.method == 'POST':
        numeroCedula = request.POST.get('Cedula')

        if (str(numeroCedula) != ''):
            try:
                agente = Agente_Transito.objects.all().filter(Cedula=numeroCedula)
                context = {'agente': agente}
                return render(request, 'Gestionar_Usuarios/nuevousuarioagtoperativo.html', context)
            except Exception as e:
                messages.warning(request, "Agente no encontrado")
                return render(request, 'Gestionar_Usuarios/nuevousuarioagtoperativo.html')
        else:
            messages.warning(request, "Ingrese Cedula a buscar")
            return render(request, 'Gestionar_Usuarios/nuevousuarioagtoperativo.html')
   else:
        return render(request, 'Gestionar_Usuarios/nuevousuarioagtoperativo.html')


def anadirfoto(request):
    if request.method == 'POST':
        agente_form = Agente_Transito_Form(request.POST, request.FILES) 
        id = request.GET['Agente_Transito']
        agente1 = Agente_Transito.objects.get(Cedula=id)
        agente1.fotoA = request.POST.get('fotoA')
        if agente1.fotoA != '':
            agente1.fotoA = request.FILES.get('fotoA')
            agente1.save()

            agente_form = Agente_Transito_Form(request.POST, request.FILES) 
            id = request.GET['Agente_Transito']
            agente = Agente_Transito.objects.all().filter(Cedula=id)
            context = {'agente': agente, 'agente_form': agente_form}
            messages.warning(request, 'Fotografía agregada con éxito')
            return render(request, 'Gestionar_Usuarios/anadirfoto.html', context)
        else:
            agente_form = Agente_Transito_Form(request.POST, request.FILES) 
            id = request.GET['Agente_Transito']
            agente = Agente_Transito.objects.all().filter(Cedula=id)
            context = {'agente': agente, 'agente_form': agente_form}
            messages.warning(request, 'Agregue una fotografía')
            return render(request, 'Gestionar_Usuarios/anadirfoto.html', context)

    else:
        agente_form = Agente_Transito_Form(request.POST, request.FILES) 
        id = request.GET['Agente_Transito']
        agente = Agente_Transito.objects.all().filter(Cedula=id)
        context = {'agente': agente, 'agente_form': agente_form}
        return render(request, 'Gestionar_Usuarios/anadirfoto.html', context)