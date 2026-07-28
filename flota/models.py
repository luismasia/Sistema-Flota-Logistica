from django.db import models
from datetime import datetime, time
from django.utils import timezone

class Empresa(models.Model):
    nombre = models.CharField(max_length=100, default='Mi Empresa')
    direccion = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Datos de la Empresa"

    def __str__(self):
        return self.nombre

class Sede(models.Model):
    ciudad = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)

    def __str__(self):
        return f"Sede - {self.ciudad}, {self.provincia}"
    
class Chofer(models.Model):
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('inactivo', 'Inactivo'),
        ('en_viaje', 'En viaje')
    ]
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_ingreso = models.DateField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default='disponible')
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='choferes', null=True, blank=True)

    class Meta:
        verbose_name = "Chofer"
        verbose_name_plural = "Choferes"

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        camion_asignado = self.camion.first()
        if camion_asignado:
            if self.estado == 'inactivo':
                camion_asignado.chofer = None
                camion_asignado.save()
            elif self.estado == 'en_viaje':
                camion_asignado.estado = 'en_viaje'
                camion_asignado.save()
            elif self.estado == 'disponible' and camion_asignado.estado == 'en_viaje':
                camion_asignado.estado = 'disponible'
                camion_asignado.save()
    
    def delete(self, *args, **kwargs):
        viajes_activos = self.viaje.filter(estado='en_curso')
        
        for viaje_afectado in viajes_activos:
            viaje_afectado.estado = 'incidente'
            viaje_afectado.save()

        super().delete(*args, **kwargs)

    @property
    def viaje_actual(self):
        return self.viaje.filter(
            estado__in=['pendiente', 'en_curso']
        ).first()
    
    @property
    def color_estado(self):
        colores = {
            'disponible': 'bg-success',
            'inactivo': 'bg-danger',            
            'en_viaje': 'bg-primary',
        }
        return colores.get(self.estado, 'bg-secondary')

class Camion(models.Model):
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('inactivo', 'Inactivo'),
        ('dañado', 'Dañado'),
        ('en_viaje', 'En viaje')
    ]
    modelo = models.CharField(max_length=100)
    patente = models.CharField(max_length=20, unique=True)
    año = models.IntegerField()
    kilometraje = models.IntegerField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default='disponible')
    chofer = models.ForeignKey(Chofer, on_delete=models.SET_NULL, null=True, blank=True, related_name='camion')
    daños = models.BooleanField(default=False)
    multas = models.BooleanField(default=False)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='camiones', null=True, blank=True)

    class Meta:
        verbose_name = "Camión"
        verbose_name_plural = "Camiones"    

    def __str__(self):
        return f"{self.modelo} - {self.patente}"
    
    def save(self, *args, **kwargs):
        if self.daños:
            self.chofer = None
            self.estado = 'dañado'
            
        elif self.chofer is None:
            self.estado = 'inactivo'
            
        elif self.estado != 'en_viaje':
            self.estado = 'disponible'
            
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        viajes_activos = self.viaje.filter(estado='en_curso')
        
        for viaje_afectado in viajes_activos:
            viaje_afectado.estado = 'incidente'
            viaje_afectado.save()
            
        super().delete(*args, **kwargs)

    @property
    def viaje_actual(self):
        return self.viaje.filter(
            estado__in=['pendiente', 'en_curso']
        ).first()
    
    @property
    def color_estado(self):
        colores = {
            'disponible': 'bg-success',
            'inactivo': 'bg-danger',            
            'en_viaje': 'bg-primary',
            'dañado': 'bg-warning text-dark',
        }
        return colores.get(self.estado, 'bg-secondary')
        
class Viaje(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_curso', 'En curso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
        ('vencido', 'Vencido'),
        ('incidente', 'Incidente'),
    ]   
    ciudad_origen = models.CharField(max_length=100)
    provincia_origen = models.CharField(max_length=100)
    ciudad_destino = models.CharField(max_length=100)
    provincia_destino = models.CharField(max_length=100)
    kilometros = models.IntegerField()
    combustible_estimado = models.IntegerField(null=True, blank=True)    
    fecha_salida = models.DateField()
    hora_salida = models.TimeField(default=time(8, 0))
    fecha_llegada = models.DateField()
    hora_llegada = models.TimeField(default=time(18, 0))
    chofer = models.ForeignKey(Chofer, on_delete=models.SET_NULL, null=True, blank=True, related_name='viaje')
    camion = models.ForeignKey(Camion, on_delete=models.SET_NULL, null=True, blank=True, related_name='viaje')
    carga = models.CharField(max_length=100)
    estado = models.CharField(max_length=30, choices=ESTADOS, default='pendiente')
    daños = models.BooleanField(default=False)
    multas = models.BooleanField(default=False)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='viajes', null=True, blank=True)

    class Meta:
        verbose_name = 'Viaje'
        verbose_name_plural = 'Viajes'

    def __str__(self):
        return f'Viaje {self.id}: {self.ciudad_origen} -> {self.ciudad_destino}'
    
    def save(self, *args, **kwargs):
        ahora = timezone.now()
        salida = timezone.make_aware(datetime.combine(self.fecha_salida, self.hora_salida))
        llegada = timezone.make_aware(datetime.combine(self.fecha_llegada, self.hora_llegada))

        if self.pk:
            viaje_viejo = Viaje.objects.get(pk=self.pk)

            if viaje_viejo.estado in ['vencido', 'completado', 'cancelado', 'incidente']:
                return
            
            if viaje_viejo.chofer and viaje_viejo.chofer != self.chofer:
                viaje_viejo.chofer.estado = 'disponible'
                viaje_viejo.chofer.save()

            if self.estado in ['cancelado', 'pendiente'] and viaje_viejo.estado not in ['cancelado', 'pendiente']:
                if self.chofer:
                    self.chofer.estado = 'disponible'
                    self.chofer.save()
                self.chofer = None

        if self.estado == 'pendiente':
            if self.chofer:
                self.camion = self.chofer.camion.first()
            else:
                self.camion = None

            if ahora >= salida and self.chofer:
                self.estado = 'en_curso'
                 
        if self.camion:
            self.camion.multas = self.multas
            self.camion.daños = self.daños
            self.camion.save()
        
        if self.estado == 'en_curso' and ahora > llegada:
            self.estado = 'completado'
        
        if self.estado == 'en_curso' and self.daños:
            self.estado = 'incidente'

        if self.estado == 'cancelado':
            if self.chofer:
                self.chofer.estado = 'disponible'
                self.chofer.save()
            self.chofer = None
            self.camion = None
        
        if ahora > salida and self.estado == 'pendiente':
            self.estado = 'vencido'
            if self.chofer:
                self.chofer.estado = 'disponible'
                self.chofer.save()
            self.chofer = None
            self.camion = None
        
        if self.chofer:
            if self.estado == 'en_curso':
                self.chofer.estado = 'en_viaje'
                self.chofer.save()
            elif self.estado in ['completado', 'incidente']:
                self.chofer.estado = 'disponible'
                self.chofer.save()

        if self.chofer:
            Viaje.objects.filter(
                chofer=self.chofer, 
                estado='pendiente'
            ).exclude(pk=self.pk).update(chofer=None, camion=None)
            
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        if self.estado == 'en_curso' and self.chofer:
            self.chofer.estado = 'disponible'
            self.chofer.save()
            
        super().delete(*args, **kwargs)

    @property
    def color_estado(self):
        colores = {
            'pendiente': 'bg-secondary',
            'en_curso': 'bg-primary',
            'completado': 'bg-success',
            'cancelado': 'bg-danger',
            'vencido': 'bg-dark',
            'incidente': 'bg-warning text-dark',
        }
        return colores.get(self.estado, 'bg-secondary')