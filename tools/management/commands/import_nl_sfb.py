
from django.core.management.base import BaseCommand
from tools.Tool_A4_NLsfB import import_nl_sfb_classification
from tools.services.nl_sfb_concepts import seed_default_concepts


class Command(BaseCommand):
    help = "Importeert NL-SfB classificatie uit Excel"

    def handle(self, *args, **options):
        import_nl_sfb_classification()
        seed_default_concepts()
        self.stdout.write(
            self.style.SUCCESS(
                "NL-SfB classificatie en zoektermen succesvol geïmporteerd"
            )
        )
