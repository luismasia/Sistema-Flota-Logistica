from django import forms
from .models import Empresa, Camion, Chofer, Viaje
from django.db.models import Q

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
        fields = ['patente', 'modelo', 'año', 'kilometraje', 'chofer']
        
        widgets = {
            'patente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ABC-123'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'año': forms.NumberInput(attrs={'class': 'form-control'}),
            'kilometraje': forms.NumberInput(attrs={'class': 'form-control'}),
            'chofer': forms.Select(attrs={'class': 'form-select'}),           
        }
    
    def __init__(self, *args, **kwargs):
        super(CamionForm, self).__init__(*args, **kwargs)
        self.fields['chofer'].empty_label = "Ninguno"
        
        if self.instance and self.instance.pk:
            if self.instance.daños:
                self.fields['chofer'].disabled = True
                self.fields['chofer'].queryset = Chofer.objects.none()
            
            elif self.instance.chofer:
                self.fields['chofer'].queryset = Chofer.objects.filter(
                    Q(estado='disponible', camion__isnull=True) | Q(id=self.instance.chofer.id)
                )
            else:
                self.fields['chofer'].queryset = Chofer.objects.filter(
                    estado='disponible', camion__isnull=True
                )

            if self.instance.estado == 'en_viaje':
                for field_name in self.fields:
                    self.fields[field_name].disabled = True
        else:
            self.fields['chofer'].queryset = Chofer.objects.filter(
                estado='disponible', camion__isnull=True
            )

class ChoferForm(forms.ModelForm):
    class Meta:
        model = Chofer
        fields = ['nombre', 'apellido', 'fecha_ingreso', 'estado']
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_ingreso': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super(ChoferForm, self).__init__(*args, **kwargs)
        
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
    
    def __init__(self, *args, **kwargs):
        super(ViajeForm, self).__init__(*args, **kwargs)
        self.fields['chofer'].empty_label = 'Seleccione un chofer'

        if self.instance and self.instance.pk:
            q_chofer = Q(camion__isnull=False, estado='disponible')
            if self.instance.chofer:
                q_chofer |= Q(id=self.instance.chofer.id)
            self.fields['chofer'].queryset = Chofer.objects.filter(q_chofer).distinct()

        else:
            self.fields['chofer'].queryset = Chofer.objects.filter(camion__isnull=False, estado='disponible').distinct()
        
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
        else:
            self.fields['daños'].disabled = True
            self.fields['multas'].disabled = True