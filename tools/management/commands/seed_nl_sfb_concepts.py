from django.core.management.base import BaseCommand

from tools.services.nl_sfb_concepts import seed_default_concepts


class Command(BaseCommand):
    help = "Voegt standaard zoektermen en NL-SfB-koppelingen toe"

    def handle(self, *args, **options):
        seed_default_concepts()
        self.stdout.write(
            self.style.SUCCESS("Standaard NL-SfB-zoektermen zijn beschikbaar")
        )
