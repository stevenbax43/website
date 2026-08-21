
from django.core.management.base import BaseCommand
from tools.Tool_A5_NLsfB import import_nl_sfb_classification


class Command(BaseCommand):
    help = "Importeert NL-SfB classificatie uit Excel"

    def handle(self, *args, **options):
        import_nl_sfb_classification()
        self.stdout.write(
            self.style.SUCCESS("NL-SfB classificatie succesvol geïmporteerd")
        )
