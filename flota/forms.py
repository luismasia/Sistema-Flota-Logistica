from django import forms
from .models import Empresa, Camion, Chofer, Viaje, Sede
from django.db.models import Q
import json

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nombre', 'direccion', 'telefono', 'email']
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class CamionForm(forms.ModelForm):
    class Meta:
        model = Camion
        fields = ['patente', 'modelo', 'año', 'kilometraje', 'sede', 'chofer',]
        
        widgets = {
            'patente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ABC-123'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'año': forms.NumberInput(attrs={'class': 'form-control'}),
            'kilometraje': forms.NumberInput(attrs={'class': 'form-control'}),
            'sede': forms.Select(attrs={'class': 'form-select'}),
            'chofer': forms.Select(attrs={'class': 'form-select'}),           
        }
    
    def __init__(self, *args, sede_contexto=None, **kwargs):
        super(CamionForm, self).__init__(*args, **kwargs)
        self.fields['chofer'].empty_label = "Ninguno"
        self.fields['sede'].empty_label = "Seleccione una sede..."
        self.fields['sede'].label_from_instance = lambda obj: obj.ciudad
        self.fields['sede'].required = True

        if sede_contexto:
            self.fields['sede'].initial = sede_contexto
            self.fields['sede'].disabled = True
            self.fields['sede'].widget.attrs['class'] += ' bg-light'

        sede_actual = sede_contexto or (self.instance.sede if self.instance and self.instance.pk else None)
        filtro_sede = Q(sede=sede_actual) if sede_actual else Q()
        filtro_chofer = Q(camion__isnull=True, estado='disponible')
        
        if self.instance and self.instance.pk:
            if self.instance.daños:
                self.fields['chofer'].disabled = True
                self.fields['chofer'].queryset = Chofer.objects.none()

            elif self.instance.chofer:
                self.fields['chofer'].queryset = Chofer.objects.filter(filtro_sede & (filtro_chofer | Q(id=self.instance.chofer.id)))
            else:
                self.fields['chofer'].queryset = Chofer.objects.filter(filtro_sede & filtro_chofer)

            if self.instance.estado == 'en_viaje':
                for field_name in self.fields:
                    self.fields[field_name].disabled = True
        else:
            self.fields['chofer'].queryset = Chofer.objects.filter(filtro_sede & filtro_chofer)

class ChoferForm(forms.ModelForm):
    class Meta:
        model = Chofer
        fields = ['nombre', 'apellido', 'fecha_ingreso', 'sede', 'estado']
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_ingreso': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'sede': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, sede_contexto=None, **kwargs):
        super(ChoferForm, self).__init__(*args, **kwargs)
        self.fields['sede'].empty_label = "Seleccione una sede..."
        self.fields['sede'].label_from_instance = lambda obj: obj.ciudad
        self.fields['sede'].required = True

        if sede_contexto:
            self.fields['sede'].initial = sede_contexto
            self.fields['sede'].disabled = True
            self.fields['sede'].widget.attrs['class'] += ' bg-light'
        
        if not self.instance.pk:
            self.fields.pop('estado')
        else:
            self.fields['estado'].choices = [
                opcion for opcion in self.fields['estado'].choices 
                if opcion[0] != 'en_viaje'
            ]
            
            if self.instance.estado == 'en_viaje':
                for field_name in self.fields:
                    self.fields[field_name].disabled = True

class ViajeForm(forms.ModelForm):
    class Meta:
        model = Viaje
        fields = [
            'ciudad_origen', 'provincia_origen', 'ciudad_destino', 'provincia_destino', 'kilometros', 'combustible_estimado', 
            'fecha_salida', 'fecha_llegada', 'chofer', 'carga', 'estado', 'daños', 'multas'
        ]
        
        widgets = {
            'ciudad_origen': forms.TextInput(attrs={'class': 'form-control'}),
            'provincia_origen': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad_destino': forms.TextInput(attrs={'class': 'form-control'}),
            'provincia_destino': forms.TextInput(attrs={'class': 'form-control'}),
            'kilometros': forms.NumberInput(attrs={'class': 'form-control'}),
            'combustible_estimado': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_salida': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_llegada': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'chofer': forms.Select(attrs={'class': 'form-select'}),
            'carga': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'daños': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'multas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),            
        }
    
    def __init__(self, *args, sede_contexto=None, **kwargs):
        super(ViajeForm, self).__init__(*args, **kwargs)
        self.fields['chofer'].empty_label = 'Seleccione un chofer'

        sede_actual = sede_contexto or (self.instance.sede if self.instance and self.instance.pk else None)
        
        if sede_contexto:
            self.fields['ciudad_origen'].initial = sede_contexto.ciudad
            self.fields['provincia_origen'].initial = sede_contexto.provincia
            self.fields['ciudad_origen'].widget.attrs['readonly'] = True
            self.fields['provincia_origen'].widget.attrs['readonly'] = True
            self.fields['ciudad_origen'].widget.attrs['class'] += ' bg-light'
            self.fields['provincia_origen'].widget.attrs['class'] += ' bg-light'
        else:
            sedes = Sede.objects.all()
            opciones_ciudades = [('', 'Seleccione ciudad de origen...')]
            mapa_provincias = {}
            for sede in sedes:
                opciones_ciudades.append((sede.ciudad, sede.ciudad))
                mapa_provincias[sede.ciudad] = sede.provincia
                
            self.fields['ciudad_origen'].widget = forms.Select(
                choices=opciones_ciudades,
                attrs={
                    'class': 'form-select',
                    'id': 'id_ciudad_origen',
                    'data-provincias': json.dumps(mapa_provincias)
                }
            )
            self.fields['provincia_origen'].widget.attrs['id'] = 'id_provincia_origen'
            self.fields['provincia_origen'].widget.attrs['readonly'] = True
            self.fields['provincia_origen'].widget.attrs['class'] += ' bg-light'

        filtro_sede = Q(sede=sede_actual) if sede_actual else Q()
        filtro_base_chofer = Q(camion__isnull=False, estado='disponible')

        if self.instance and self.instance.pk and self.instance.chofer:
            self.fields['chofer'].queryset = Chofer.objects.filter(
                (filtro_sede & filtro_base_chofer) | Q(id=self.instance.chofer.id)
            ).distinct()
        else:
            self.fields['chofer'].queryset = Chofer.objects.filter(filtro_sede & filtro_base_chofer).distinct()
        
        estado_actual = self.instance.estado if self.instance and self.instance.pk else 'pendiente'
        
        self.fields['estado'].choices = [
            opcion for opcion in self.fields['estado'].choices 
            if opcion[0] != 'vencido' 
            and (opcion[0] != 'en_curso' or opcion[0] == estado_actual)
            and (opcion[0] != 'completado' or estado_actual in ['en_curso', 'completado'])
            and (opcion[0] != 'incidente' or opcion[0] == estado_actual)
        ]
        
        if self.instance and not self.instance.chofer:
            self.fields['estado'].choices = [
                ('pendiente', 'Pendiente'),
                ('cancelado', 'Cancelado'),
            ]
        
        if self.instance and self.instance.estado == 'en_curso':
            for field_name in self.fields:
                if field_name not in ['daños', 'multas']:
                    self.fields[field_name].disabled = True
                    self.fields[field_name].required = False
        else:
            self.fields['daños'].disabled = True
            self.fields['multas'].disabled = True

class SedeForm(forms.ModelForm):
    class Meta:
        model = Sede
        fields = ['ciudad', 'provincia']
        
        widgets = {
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'provincia': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(SedeForm, self).__init__(*args, **kwargs)