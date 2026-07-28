from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from .models import Empresa, Camion, Chofer, Viaje, Sede
from .forms import EmpresaForm, CamionForm, ChoferForm, ViajeForm, SedeForm
from datetime import date
from django.db.models import Q, Case, When, Value, IntegerField, Value as V
from django.db.models.functions import Concat
from django import forms

def actualizar_estados_flota(sede=None):  
    hoy = date.today()
    filtro_sede = Q(sede=sede) if sede else Q()

    viajes_a_iniciar = Viaje.objects.filter(
        filtro_sede,
        estado='pendiente',
        fecha_salida__lte=hoy,
        chofer__isnull=False
    )

    for viaje in viajes_a_iniciar:
        viaje.estado = 'en_curso'
        if not viaje.camion and viaje.chofer.camion.first():
            viaje.camion = viaje.chofer.camion.first()
        if viaje.chofer:
            viaje.chofer.estado = 'en_viaje'
            viaje.chofer.save()
        viaje.save()

    viajes_vencidos = Viaje.objects.filter(
        filtro_sede,
        estado='pendiente',
        fecha_salida__lt=hoy,
        chofer__isnull=True
    )

    for viaje in viajes_vencidos:
        viaje.estado = 'vencido'
        if viaje.chofer:
            viaje.chofer.estado = 'disponible'
            viaje.chofer.save()
        viaje.chofer = None
        viaje.camion = None
        viaje.save()

    viajes_a_completar = Viaje.objects.filter(
        filtro_sede,
        estado='en_curso',
        fecha_llegada__lt=hoy
    )

    for viaje in viajes_a_completar:
        viaje.estado = 'completado'
        if viaje.chofer:
            viaje.chofer.estado = 'disponible'
            viaje.chofer.save()
        viaje.save()

class FiltrosFlotaMixin:
    def aplicar_filtros_comunes(self, queryset):
        f_sede = self.request.GET.get('sede')
        f_estado = self.request.GET.get('estado')
        
        if f_sede:
            queryset = queryset.filter(sede_id=f_sede)
        if f_estado:
            queryset = queryset.filter(estado=f_estado)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sedes'] = Sede.objects.all()
        context['filtros_actuales'] = self.request.GET
        
        if hasattr(self.model, 'ESTADOS'):
            estados_existentes = self.model.objects.values_list('estado', flat=True).distinct()
            context['estados_disponibles'] = [
                (clave, valor) for clave, valor in self.model.ESTADOS if clave in estados_existentes
            ]
        return context

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
        context['total_sedes'] = Sede.objects.count()
        return context

class CamionListView(FiltrosFlotaMixin, ListView):
    model = Camion
    template_name = 'camiones/camion_list.html'
    context_object_name = 'camiones'

    def get_queryset(self):
        actualizar_estados_flota()
        queryset = Camion.objects.all()
        queryset = self.aplicar_filtros_comunes(queryset)

        f_busqueda = self.request.GET.get('busqueda', '').strip()
        f_marca = self.request.GET.get('marca')
        f_año = self.request.GET.get('año')
        f_daños = self.request.GET.get('daños')
        f_multas = self.request.GET.get('multas')

        if f_busqueda:
            queryset = queryset.annotate(
                chofer_nombre_completo=Concat('chofer__nombre', V(' '), 'chofer__apellido'),
                chofer_apellido_nombre=Concat('chofer__apellido', V(' '), 'chofer__nombre')
            ).filter(
                Q(patente__icontains=f_busqueda) |
                Q(modelo__icontains=f_busqueda) |
                Q(chofer__nombre__icontains=f_busqueda) |
                Q(chofer__apellido__icontains=f_busqueda) |
                Q(chofer_nombre_completo__icontains=f_busqueda) |
                Q(chofer_apellido_nombre__icontains=f_busqueda)
            )
        if f_marca:
            queryset = queryset.filter(modelo__icontains=f_marca)
        if f_año:
            queryset = queryset.filter(año=f_año)

        filtros_incidentes = Q()
        if f_daños == 'on':
            filtros_incidentes |= Q(daños=True)
        if f_multas == 'on':
            filtros_incidentes |= Q(multas=True)
        
        if filtros_incidentes:
            queryset = queryset.filter(filtros_incidentes)
 
        return queryset.annotate(
            prioridad_estado=Case(
                When(estado='en_viaje', then=Value(1)),
                When(estado='disponible', then=Value(2)),
                When(estado='dañado', then=Value(3)),
                When(estado='inactivo', then=Value(4)),
                default=Value(5),
                output_field=IntegerField(),
            )
        ).order_by('prioridad_estado', 'sede__ciudad')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['marcas'] = [
            'Scania', 'Mercedes Benz', 'Volvo', 'Iveco', 
            'Renault', 'Ford', 'Volkswagen', 'Freightliner', 'Mack',
            'Peterbilt', 'MAN', 'DAF', 'Dodge', 'Fiat'
        ]
        context['años_disponibles'] = Camion.objects.values_list('año', flat=True).distinct().order_by('-año')
        context['filtros_actuales'] = self.request.GET
        return context

class CamionDetailView(DetailView):
    model = Camion
    template_name = 'camiones/camion_detail.html'
    context_object_name = 'camion'

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            sede_id = self.kwargs.get('sede_id')
    
            if sede_id:
                context['sede_actual'] = get_object_or_404(Sede, pk=sede_id)
                context['cancel_url'] = reverse('sede_camion_list', kwargs={'sede_id': sede_id})
                context['edit_url'] = reverse('sede_camion_update', kwargs={'sede_id': sede_id, 'pk': self.object.pk})
            else:
                context['cancel_url'] = reverse('camion_list')
                context['edit_url'] = reverse('camion_update', kwargs={'pk': self.object.pk})
            return context

class CamionCreateView(CreateView):
    model = Camion
    form_class = CamionForm
    template_name = 'form_generico.html'
    success_url = reverse_lazy('camion_list')

    def form_valid(self, form):
        sede_id = self.kwargs.get('sede_id')
        if sede_id:
            sede_actual = get_object_or_404(Sede, pk=sede_id)
            form.instance.sede = sede_actual
        return super().form_valid(form)

    def get_success_url(self):
        sede_id = self.kwargs.get('sede_id')
        if sede_id:
            return reverse('sede_camion_list', kwargs={'sede_id': sede_id})
        return reverse('camion_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar nuevo camión'
        sede_id = self.kwargs.get('sede_id')
        if sede_id:
            context['cancel_url'] = reverse('sede_camion_list', kwargs={'sede_id': sede_id})
        else:
            context['cancel_url'] = reverse('camion_list')
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        sede_id = self.kwargs.get('sede_id')
        if sede_id:
            kwargs['sede_contexto'] = get_object_or_404(Sede, pk=sede_id)
        elif self.object and hasattr(self.object, 'sede') and self.object.sede:
            kwargs['sede_contexto'] = self.object.sede
        return kwargs

class CamionUpdateView(UpdateView):
    model = Camion
    form_class = CamionForm
    template_name = 'form_generico.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        sede_id = self.kwargs.get('sede_id')
        if sede_id:
            kwargs['sede_contexto'] = get_object_or_404(Sede, pk=sede_id)
        elif self.object and hasattr(self.object, 'sede') and self.object.sede:
            kwargs['sede_contexto'] = self.object.sede
        return kwargs

    def get_success_url(self):
        sede_id = self.kwargs.get('sede_id')
        if sede_id:
            return reverse('sede_camion_list', kwargs={'sede_id': sede_id})
        return reverse('camion_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Actualizar datos de {self.object.modelo} - {self.object.patente}'
        sede_id = self.kwargs.get('sede_id')
        if sede_id:
            context['cancel_url'] = reverse('sede_camion_list', kwargs={'sede_id': sede_id})
        else:
            context['cancel_url'] = reverse('camion_list')
        return context

class CamionDeleteView(DeleteView):
    model = Camion
    template_name = 'confirmar_eliminacion.html'

    def get_success_url(self):
        siguiente_url = self.request.POST.get('next')
    
        if siguiente_url:
            return siguiente_url
            
        if self.object.sede:
            return reverse('sede_camion_list', kwargs={'sede_id': self.object.sede.id})
        return reverse('camion_list')

class ChoferListView(FiltrosFlotaMixin, ListView):
    model = Chofer
    template_name = 'choferes/chofer_list.html'
    context_object_name = 'choferes'

    def get_queryset(self):
        actualizar_estados_flota()
        queryset = Chofer.objects.all()
        queryset = self.aplicar_filtros_comunes(queryset)

        f_busqueda = self.request.GET.get('busqueda', '').strip()
        if f_busqueda:
            queryset = queryset.annotate(
                nombre_completo=Concat('nombre', V(' '), 'apellido'),
                apellido_nombre=Concat('apellido', V(' '), 'nombre')
            ).filter(
                Q(nombre__icontains=f_busqueda) |
                Q(apellido__icontains=f_busqueda) |
                Q(nombre_completo__icontains=f_busqueda) |
                Q(apellido_nombre__icontains=f_busqueda)
            )

        f_año = self.request.GET.get('año')
        if f_año:
            queryset = queryset.filter(fecha_ingreso__year=f_año)

        return queryset.annotate(
            prioridad_estado=Case(
                When(estado='disponible', then=Value(1)),
                When(estado='inactivo', then=Value(2)),
                When(estado='en_viaje', then=Value(3)),
                default=Value(4),
                output_field=IntegerField(),
            )
        ).order_by('prioridad_estado', 'sede__ciudad', 'apellido', 'nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['años_disponibles'] = Chofer.objects.values_list('fecha_ingreso__year', flat=True).distinct().order_by('-fecha_ingreso__year')
        return context

class ChoferDetailView(DetailView):
    model = Chofer
    template_name = 'choferes/chofer_detail.html'
    context_object_name = 'chofer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sede_id = self.kwargs.get('sede_id')

        if sede_id:
            context['sede_actual'] = get_object_or_404(Sede, pk=sede_id)
            context['cancel_url'] = reverse('sede_chofer_list', kwargs={'sede_id': sede_id})
            context['edit_url'] = reverse('sede_chofer_update', kwargs={'sede_id': sede_id, 'pk': self.object.pk})
        else:
            context['cancel_url'] = reverse('chofer_list')
            context['edit_url'] = reverse('chofer_update', kwargs={'pk': self.object.pk})
        return context

class ChoferCreateView(CreateView):
    model = Chofer
    form_class = ChoferForm
    template_name = 'form_generico.html'
    success_url = reverse_lazy('chofer_list')

    def form_valid(self, form):
            sede_id = self.kwargs.get('sede_id')
            if sede_id:
                sede_actual = get_object_or_404(Sede, pk=sede_id)
                form.instance.sede = sede_actual
            return super().form_valid(form)
    
    def get_success_url(self):
        sede_id = self.kwargs.get('sede_id')
        if sede_id:
            return reverse('sede_chofer_list', kwargs={'sede_id': sede_id})
        return reverse('chofer_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar nuevo chofer'
        sede_id = self.kwargs.get('sede_id')
        if sede_id:
            context['cancel_url'] = reverse('sede_chofer_list', kwargs={'sede_id': sede_id})
        else:
            context['cancel_url'] = reverse('chofer_list')
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        sede_id = self.kwargs.get('sede_id')
        if sede_id:
            kwargs['sede_contexto'] = get_object_or_404(Sede, pk=sede_id)
        return kwargs

class ChoferUpdateView(UpdateView):
    model = Chofer
    form_class = ChoferForm
    template_name = 'form_generico.html'

    def get_form_kwargs(self):
            kwargs = super().get_form_kwargs()
            sede_id = self.kwargs.get('sede_id')
            if sede_id:
                kwargs['sede_contexto'] = get_object_or_404(Sede, pk=sede_id)
            elif self.object and hasattr(self.object, 'sede') and self.object.sede:
                kwargs['sede_contexto'] = self.object.sede
            return kwargs
    
    def get_success_url(self):
        sede_id = self.kwargs.get('sede_id')
        if sede_id:
            return reverse('sede_chofer_list', kwargs={'sede_id': sede_id})
        return reverse('chofer_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Actualizar datos de {self.object.apellido}, {self.object.nombre}'
        sede_id = self.kwargs.get('sede_id')
        if sede_id:
            context['cancel_url'] = reverse('sede_chofer_list', kwargs={'sede_id': sede_id})
        else:
            context['cancel_url'] = reverse('chofer_list')
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        sede_id = self.kwargs.get('sede_id')
        if sede_id:
            kwargs['sede_contexto'] = get_object_or_404(Sede, pk=sede_id)
        return kwargs

class ChoferDeleteView(DeleteView):
    model = Chofer
    template_name = 'confirmar_eliminacion.html'

    def get_success_url(self):
        siguiente_url = self.request.POST.get('next')
        
        if siguiente_url:
            return siguiente_url
            
        if self.object.sede:
            return reverse('sede_chofer_list', kwargs={'sede_id': self.object.sede.id})
        return reverse('chofer_list')

class ViajeListView(FiltrosFlotaMixin, ListView):
    model = Viaje
    template_name = 'viajes/viaje_list.html'
    context_object_name = 'viajes'

    def get_queryset(self):
        actualizar_estados_flota()
        queryset = Viaje.objects.all()
        queryset = self.aplicar_filtros_comunes(queryset)

        f_busqueda = self.request.GET.get('busqueda', '').strip()
        f_chofer = self.request.GET.get('chofer')
        f_camion = self.request.GET.get('camion')
        f_fecha = self.request.GET.get('fecha_salida')
        f_destino = self.request.GET.get('destino')

        if f_busqueda:
            queryset = queryset.annotate(
                chofer_nombre_completo=Concat('chofer__nombre', V(' '), 'chofer__apellido'),
                chofer_apellido_nombre=Concat('chofer__apellido', V(' '), 'chofer__nombre')
            ).filter(
                Q(carga__icontains=f_busqueda) |
                Q(camion__patente__icontains=f_busqueda) |
                Q(chofer__nombre__icontains=f_busqueda) |
                Q(chofer__apellido__icontains=f_busqueda) |
                Q(chofer_nombre_completo__icontains=f_busqueda) |
                Q(chofer_apellido_nombre__icontains=f_busqueda)
            )

        if f_chofer:
            queryset = queryset.filter(chofer_id=f_chofer)
        if f_camion:
            queryset = queryset.filter(camion_id=f_camion)
        if f_fecha:
            queryset = queryset.filter(fecha_salida=f_fecha)
        if f_destino:
            queryset = queryset.filter(ciudad_destino=f_destino)

        return queryset.annotate(
            prioridad_estado=Case(
                When(estado='en_curso', then=Value(1)),
                When(estado='pendiente', then=Value(2)),
                When(estado='incidente', then=Value(3)),
                When(estado='vencido', then=Value(4)),
                When(estado='completado', then=Value(5)),
                When(estado='cancelado', then=Value(6)),
                default=Value(7),
                output_field=IntegerField(),
            )
        ).order_by('prioridad_estado', 'fecha_salida', 'fecha_llegada', 'ciudad_origen')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['choferes'] = Chofer.objects.all().order_by('apellido', 'nombre')
        context['camiones'] = Camion.objects.all().order_by('patente')
        context['ciudades_destino'] = Viaje.objects.values_list('ciudad_destino', flat=True).distinct().order_by('ciudad_destino')
        return context
    
class ViajeDetailView(DetailView):
    model = Viaje
    template_name = 'viajes/viaje_detail.html'
    context_object_name = 'viaje'

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            sede_id = self.kwargs.get('sede_id')
    
            if sede_id:
                context['sede_actual'] = get_object_or_404(Sede, pk=sede_id)
                context['cancel_url'] = reverse('sede_viaje_list', kwargs={'sede_id': sede_id})
                context['edit_url'] = reverse('sede_viaje_update', kwargs={'sede_id': sede_id, 'pk': self.object.pk})
            else:
                context['cancel_url'] = reverse('viaje_list')
                context['edit_url'] = reverse('viaje_update', kwargs={'pk': self.object.pk})
            return context

class ViajeCreateView(CreateView):
    model = Viaje
    form_class = ViajeForm
    template_name = 'form_generico.html'
    success_url = reverse_lazy('viaje_list')

    def form_valid(self, form):
        sede_id = self.kwargs.get('sede_id')
        if sede_id:
            sede_actual = get_object_or_404(Sede, pk=sede_id)
            form.instance.sede = sede_actual
            form.instance.ciudad_origen = sede_actual.ciudad
            form.instance.provincia_origen = sede_actual.provincia
        else:
            ciudad_elegida = form.cleaned_data.get('ciudad_origen')
            if ciudad_elegida:
                sede_encontrada = Sede.objects.filter(ciudad=ciudad_elegida).first()
                if sede_encontrada:
                    form.instance.sede = sede_encontrada
        return super().form_valid(form)

    def get_success_url(self):
        sede_id = self.kwargs.get('sede_id')
        if sede_id:
            return reverse('sede_viaje_list', kwargs={'sede_id': sede_id})
        return reverse('viaje_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar nuevo viaje'
        sede_id = self.kwargs.get('sede_id')
        if sede_id:
            context['cancel_url'] = reverse('sede_viaje_list', kwargs={'sede_id': sede_id})
        else:
            context['cancel_url'] = reverse('viaje_list')
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        sede_id = self.kwargs.get('sede_id')
        if sede_id:
            kwargs['sede_contexto'] = get_object_or_404(Sede, pk=sede_id)
        elif self.object and self.object.sede:
            kwargs['sede_contexto'] = self.object.sede
        return kwargs

class ViajeUpdateView(UpdateView):
    model = Viaje
    form_class = ViajeForm
    template_name = 'form_generico.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        sede_id = self.kwargs.get('sede_id')
        if sede_id:
            kwargs['sede_contexto'] = get_object_or_404(Sede, pk=sede_id)
        return kwargs

    def form_valid(self, form):
        sede_id = self.kwargs.get('sede_id')
        if sede_id:
            sede_actual = get_object_or_404(Sede, pk=sede_id)
            form.instance.sede = sede_actual
            form.instance.ciudad_origen = sede_actual.ciudad
            form.instance.provincia_origen = sede_actual.provincia
        else:
            ciudad_elegida = form.cleaned_data.get('ciudad_origen')
            if ciudad_elegida:
                sede_encontrada = Sede.objects.filter(ciudad=ciudad_elegida).first()
                if sede_encontrada:
                    form.instance.sede = sede_encontrada
                    form.instance.provincia_origen = sede_encontrada.provincia
        return super().form_valid(form)

    def get_success_url(self):
        sede_id = self.kwargs.get('sede_id')
        if sede_id:
            return reverse('sede_viaje_list', kwargs={'sede_id': sede_id})
        return reverse('viaje_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Actualizar datos del Viaje #{self.object.id}'
        sede_id = self.kwargs.get('sede_id')
        if sede_id:
            context['cancel_url'] = reverse('sede_viaje_list', kwargs={'sede_id': sede_id})
        else:
            context['cancel_url'] = reverse('viaje_list')
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

    def get_success_url(self):
        siguiente_url = self.request.POST.get('next')
        
        if siguiente_url:
            return siguiente_url
            
        if self.object.sede:
            return reverse('sede_viaje_list', kwargs={'sede_id': self.object.sede.id})
        return reverse('viaje_list')

class SedeListView(ListView):
    model = Sede
    template_name = 'sedes/sede_list.html'
    context_object_name = 'sedes'

class SedeDetailView(DetailView):
    model = Sede
    template_name = 'sedes/sede_detail.html'
    context_object_name = 'sede'

class SedeCreateView(CreateView):
    model = Sede
    form_class = SedeForm
    template_name = 'form_generico.html'
    success_url = reverse_lazy('sede_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar nueva sede'
        context['cancel_url'] = reverse_lazy('sede_list')
        return context

class SedeUpdateView(UpdateView):
    model = Sede
    form_class = SedeForm
    template_name = 'form_generico.html'
    success_url = reverse_lazy('sede_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Actualizar datos de Sede {self.object.ciudad}'
        context['cancel_url'] = reverse_lazy('sede_detail', kwargs={'pk': self.object.pk})
        return context

    def get_success_url(self):
        return reverse_lazy('sede_detail', kwargs={'pk': self.object.pk})

class SedeDeleteView(DeleteView):
    model = Sede
    template_name = 'confirmar_eliminacion.html'
    success_url = reverse_lazy('sede_list')

    def get_success_url(self):
        return reverse('sede_list')

class CamionSedeListView(CamionListView):

    def get_queryset(self):
        self.sede = get_object_or_404(Sede, pk=self.kwargs['sede_id'])
        return super().get_queryset().filter(sede=self.sede)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sede_actual'] = self.sede
        return context

class ChoferSedeListView(ChoferListView):

    def get_queryset(self):
        self.sede = get_object_or_404(Sede, pk=self.kwargs['sede_id'])
        return super().get_queryset().filter(sede=self.sede)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sede_actual'] = self.sede
        return context

class ViajeSedeListView(ViajeListView):

    def get_queryset(self):
        self.sede = get_object_or_404(Sede, pk=self.kwargs['sede_id'])
        return super().get_queryset().filter(sede=self.sede)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sede_actual'] = self.sede
        return context

class TrasladoView(UpdateView):
    template_name = 'form_generico.html'
    fields = ['sede']
    
    nombre_modelo = ""  
    url_general = ""    
    url_sede = ""       

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        form.fields['sede'].widget = forms.Select(attrs={'class': 'form-select'})
        form.fields['sede'].empty_label = "Seleccione nueva sede"
        form.fields['sede'].label_from_instance = lambda obj: obj.ciudad
        
        if self.object and self.object.sede:
            form.fields['sede'].queryset = Sede.objects.exclude(id=self.object.sede.id)
        return form

    def dispatch(self, request, *args, **kwargs):
        objeto = self.get_object()
        if objeto.estado == 'en_viaje':
            messages.error(request, f"No podés trasladar a {self.nombre_modelo.lower()} '{str(objeto)}' porque se encuentra en viaje.")
            return redirect(self.url_general)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sede_actual_str = self.object.sede.ciudad if self.object.sede else "Sin sede"
        context['titulo'] = f'Trasladar {self.nombre_modelo}: {str(self.object)} (Sede actual: {sede_actual_str})'
        
        sede_id = self.kwargs.get('sede_id')
        context['cancel_url'] = reverse(self.url_sede, kwargs={'sede_id': sede_id}) if sede_id else reverse(self.url_general)
        return context

    def get_success_url(self):
        messages.success(self.request, f"{self.nombre_modelo} trasladado exitosamente a la sede {self.object.sede.ciudad}.")
        sede_id = self.kwargs.get('sede_id')
        return reverse(self.url_sede, kwargs={'sede_id': sede_id}) if sede_id else reverse(self.url_general)

class CamionTrasladoView(TrasladoView):
    model = Camion
    nombre_modelo = "Camión"
    url_general = 'camion_list'
    url_sede = 'sede_camion_list'

class ChoferTrasladoView(TrasladoView):
    model = Chofer
    nombre_modelo = "Chofer"
    url_general = 'chofer_list'
    url_sede = 'sede_chofer_list'

class MantenimientoView(View):
    template_name = 'camiones/mantenimiento.html'

    def get(self, request, *args, **kwargs):
        sede_id = kwargs.get('sede_id')
        sede_actual = get_object_or_404(Sede, pk=sede_id) if sede_id else None
        filtro_sede = Q(sede=sede_actual) if sede_actual else Q()

        camiones_danados = Camion.objects.filter(
            filtro_sede, 
            estado='dañado'
        ).distinct()

        camiones_multados = Camion.objects.filter(
            filtro_sede, 
            multas=True
        ).distinct()

        context = {
            'titulo': f'Central de Mantenimiento y Multas {"- Sede " + sede_actual.ciudad if sede_actual else ""}',
            'camiones_danados': camiones_danados,
            'camiones_multados': camiones_multados,
            'sede_actual': sede_actual,
            'volver_url': reverse('sede_camion_list', kwargs={'sede_id': sede_id}) if sede_id else reverse('camion_list')
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        sede_id = kwargs.get('sede_id')
        accion = request.POST.get('accion')
        
        if accion == 'reparar':
            ids_seleccionados = request.POST.getlist('camiones_taller')
            if ids_seleccionados:
                filas_actualizadas = Camion.objects.filter(id__in=ids_seleccionados).update(estado='inactivo', daños=False)
                messages.success(request, f"¡Éxito! Se enviaron {filas_actualizadas} camión(es) al taller.")
            else:
                messages.warning(request, "No seleccionaste ningún camión para reparar.")
        elif accion == 'pagar_multas':
            ids_seleccionados = request.POST.getlist('camiones_multas')
            if ids_seleccionados:
                filas_actualizadas = Camion.objects.filter(id__in=ids_seleccionados).update(multas=False)
                messages.success(request, f"¡Éxito! Se pagaron las infracciones de {filas_actualizadas} camión(es).")
            else:
                messages.warning(request, "No seleccionaste ningún camión.")
        if sede_id:
            return redirect('sede_mantenimiento', sede_id=sede_id)
        return redirect('mantenimiento')