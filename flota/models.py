from django.db import models

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
    nombre = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} - {self.ciudad}, {self.provincia}"
    
class Chofer(models.Model):
    ESTADOS = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_ingreso = models.DateField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default='activo')

    class Meta:
        verbose_name = "Chofer"
        verbose_name_plural = "Choferes"

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"

class Camion(models.Model):
    ESTADOS = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    modelo = models.CharField(max_length=100)
    patente = models.CharField(max_length=20, unique=True)
    año = models.IntegerField()
    kilometraje = models.IntegerField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default='activo')
    chofer_asignado = models.ForeignKey(Chofer, on_delete=models.SET_NULL, null=True, blank=True, related_name='camion')

    class Meta:
        verbose_name = "Camión"
        verbose_name_plural = "Camiones"    

    def __str__(self):
        return f"{self.modelo} {self.patente}"

class Viaje(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_curso', 'En curso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]   
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    kilometros = models.IntegerField()
    fecha = models.DateField()
    chofer = models.ForeignKey(Chofer, on_delete=models.SET_NULL, null=True, related_name='viaje')
    camion_asignado = models.ForeignKey(Camion, on_delete=models.SET_NULL, null=True, related_name='viaje')
    carga = models.CharField(max_length=100)
    estado = models.CharField(max_length=30, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"Viaje {self.id}: {self.origen} -> {self.destino}"