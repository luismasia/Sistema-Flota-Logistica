from django.contrib import admin
from .models import Sede, Chofer, Camion, Viaje, Empresa

admin.site.register(Empresa)

@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ('ciudad', 'provincia')
    list_filter = ('provincia',)
    search_fields = ('ciudad', 'provincia')

@admin.register(Chofer)
class ChoferAdmin(admin.ModelAdmin):
    list_display = ('apellido', 'nombre', 'estado', 'fecha_ingreso')
    list_filter = ('estado',)
    search_fields = ('apellido', 'nombre')

@admin.register(Camion)
class CamionAdmin(admin.ModelAdmin):
    list_display = ('patente', 'modelo', 'año', 'estado', 'chofer')
    list_filter = ('estado', 'modelo')
    search_fields = ('patente', 'modelo')

@admin.register(Viaje)
class ViajeAdmin(admin.ModelAdmin):
    list_display = ('id', 'ciudad_origen', 'ciudad_destino', 'fecha_salida', 'fecha_llegada', 'estado', 'chofer', 'camion')
    list_filter = ('estado', 'fecha_salida', 'fecha_llegada')
    search_fields = ('ciudad_origen', 'provincia_origen', 'ciudad_destino', 'provincia_destino', 'carga')
    date_hierarchy = 'fecha_salida'