from django.urls import path
from . import views
urlpatterns = [
    path('', views.InicioView.as_view(), name='inicio'),
    path('configuracion/empresa/', views.EmpresaUpdateView.as_view(), name='empresa_config'),    
    path('camiones/', views.CamionListView.as_view(), name='camion_list'),
    path('camiones/nuevo/', views.CamionCreateView.as_view(), name='camion_create'),
    path('camiones/<int:pk>/', views.CamionDetailView.as_view(), name='camion_detail'),
    path('camiones/<int:pk>/editar/', views.CamionUpdateView.as_view(), name='camion_update'),
    path('camiones/<int:pk>/eliminar/', views.CamionDeleteView.as_view(), name='camion_delete'),
    path('choferes/', views.ChoferListView.as_view(), name='chofer_list'),
    path('choferes/nuevo/', views.ChoferCreateView.as_view(), name='chofer_create'),
    path('choferes/<int:pk>/', views.ChoferDetailView.as_view(), name='chofer_detail'),
    path('choferes/<int:pk>/editar/', views.ChoferUpdateView.as_view(), name='chofer_update'),
    path('choferes/<int:pk>/eliminar/', views.ChoferDeleteView.as_view(), name='chofer_delete'),
    path('viajes/', views.ViajeListView.as_view(), name='viaje_list'),
    path('viajes/nuevo/', views.ViajeCreateView.as_view(), name='viaje_create'),
    path('viajes/<int:pk>/', views.ViajeDetailView.as_view(), name='viaje_detail'),
    path('viajes/<int:pk>/editar/', views.ViajeUpdateView.as_view(), name='viaje_update'),
    path('viajes/<int:pk>/eliminar/', views.ViajeDeleteView.as_view(), name='viaje_delete'),    
]