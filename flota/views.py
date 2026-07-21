from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect
from django.contrib import messages
from .models import Empresa, Camion, Chofer, Viaje
from .forms import EmpresaForm, CamionForm, ChoferForm, ViajeForm

class EmpresaUpdateView(UpdateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'form_generico.html'
    success_url = reverse_lazy('inicio')

    def get_object(self, queryset=None):
        obj, created = Empresa.objects.get_or_create(id=1)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Configuración de la Empresa'
        context['cancel_url'] = reverse_lazy('inicio')
        return context

class InicioView(TemplateView):
    template_name = 'inicio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_camiones'] = Camion.objects.count()
        context['total_choferes'] = Chofer.objects.count()
        context['total_viajes'] = Viaje.objects.count()
        return context

class CamionListView(ListView):
    model = Camion
    template_name = 'camiones/camion_list.html'
    context_object_name = 'camiones'

class CamionDetailView(DetailView):
    model = Camion
    template_name = 'camiones/camion_detail.html'
    context_object_name = 'camion'

class CamionCreateView(CreateView):
    model = Camion
    form_class = CamionForm
    template_name = 'form_generico.html'
    success_url = reverse_lazy('camion_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar nuevo camión'
        context['cancel_url'] = reverse_lazy('camion_list')
        return context

class CamionUpdateView(UpdateView):
    model = Camion
    form_class = CamionForm
    template_name = 'form_generico.html'
    success_url = reverse_lazy('camion_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Actualizar datos de {self.object.modelo} - {self.object.patente}'
        context['cancel_url'] = reverse_lazy('camion_list')
        return context

class CamionDeleteView(DeleteView):
    model = Camion
    template_name = 'confirmar_eliminacion.html'
    success_url = reverse_lazy('camion_list')

class ChoferListView(ListView):
    model = Chofer
    template_name = 'choferes/chofer_list.html'
    context_object_name = 'choferes'

class ChoferDetailView(DetailView):
    model = Chofer
    template_name = 'choferes/chofer_detail.html'
    context_object_name = 'chofer'

class ChoferCreateView(CreateView):
    model = Chofer
    form_class = ChoferForm
    template_name = 'form_generico.html'
    success_url = reverse_lazy('chofer_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar nuevo chofer'
        context['cancel_url'] = reverse_lazy('camion_list')
        return context    

class ChoferUpdateView(UpdateView):
    model = Chofer
    form_class = ChoferForm
    template_name = 'form_generico.html'
    success_url = reverse_lazy('chofer_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Actualizar datos de {self.object.apellido}, {self.object.nombre}'
        context['cancel_url'] = reverse_lazy('chofer_list')
        return context

class ChoferDeleteView(DeleteView):
    model = Chofer
    template_name = 'confirmar_eliminacion.html'
    success_url = reverse_lazy('chofer_list')

class ViajeListView(ListView):
    model = Viaje
    template_name = 'viajes/viaje_list.html'
    context_object_name = 'viajes'

class ViajeDetailView(DetailView):
    model = Viaje
    template_name = 'viajes/viaje_detail.html'
    context_object_name = 'viaje'

class ViajeCreateView(CreateView):
    model = Viaje
    form_class = ViajeForm
    template_name = 'form_generico.html'
    success_url = reverse_lazy('viaje_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar nuevo viaje'
        context['cancel_url'] = reverse_lazy('viaje_list')
        return context    

class ViajeUpdateView(UpdateView):
    model = Viaje
    form_class = ViajeForm
    template_name = 'form_generico.html'
    success_url = reverse_lazy('viaje_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Actualizar datos del Viaje #{self.object.id}'
        context['cancel_url'] = reverse_lazy('viaje_list')
        return context
    
    def dispatch(self, request, *args, **kwargs):
        viaje = self.get_object()
        if viaje.estado in ['vencido', 'completado', 'cancelado', 'incidente']:
            messages.error(request, "No podés editar un viaje que ya fue cerrado.")
            return redirect('viajes_list')
            
        return super().dispatch(request, *args, **kwargs)

class ViajeDeleteView(DeleteView):
    model = Viaje
    template_name = 'confirmar_eliminacion.html'
    success_url = reverse_lazy('viaje_list')