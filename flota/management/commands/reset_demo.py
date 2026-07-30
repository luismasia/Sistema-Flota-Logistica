from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Resetea la base de datos de la demo a su estado inicial"

    def handle(self, *args, **options):
        call_command('flush', '--noinput')
        call_command('loaddata', 'flota/fixtures/demo_data.json')
        self.stdout.write(self.style.SUCCESS("Demo reseteada correctamente."))