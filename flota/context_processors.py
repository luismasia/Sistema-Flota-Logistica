from django.conf import settings
from .models import Empresa

def informacion_empresa(request):
    empresa = Empresa.objects.first()
    return {
        'INFO_EMPRESA': empresa
    }