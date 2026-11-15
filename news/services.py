import logging

from .news_scrape import (
    EenWInstallatieTechniekNews_extract,
    InstallatieNews_extract,
    WeiiNews_extract,
)

logger = logging.getLogger('django')


class NewsUpdateError(Exception):
    pass


def update_news(author=None):
    scrapers = (
        ('Installatie.nl', InstallatieNews_extract),
        ('WEii', WeiiNews_extract),
        ('E&W Installatietechniek', EenWInstallatieTechniekNews_extract),
    )
    failures = []

    for source, scraper in scrapers:
        try:
            scraper(author)
        except Exception:
            logger.exception('News update failed for %s', source)
            failures.append(source)

    if failures:
        raise NewsUpdateError(
            'News update failed for: ' + ', '.join(failures)
        )
