from django.core.management.base import BaseCommand, CommandError

from news.services import NewsUpdateError, update_news


class Command(BaseCommand):
    help = 'Fetch the latest news articles from configured sources.'

    def handle(self, *args, **options):
        self.stdout.write('Starting news update...')
        try:
            update_news()
        except NewsUpdateError as error:
            raise CommandError(str(error)) from error

        self.stdout.write(self.style.SUCCESS('News update completed.'))
