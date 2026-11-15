from io import StringIO
from unittest.mock import patch

from django.core.management import call_command, CommandError
from django.test import SimpleTestCase

from .services import NewsUpdateError, update_news


class NewsUpdateTests(SimpleTestCase):
    @patch('news.services.EenWInstallatieTechniekNews_extract')
    @patch('news.services.WeiiNews_extract')
    @patch('news.services.InstallatieNews_extract')
    def test_update_runs_each_scraper_without_an_author(
        self,
        installatie_scraper,
        weii_scraper,
        ew_scraper,
    ):
        update_news()

        installatie_scraper.assert_called_once_with(None)
        weii_scraper.assert_called_once_with(None)
        ew_scraper.assert_called_once_with(None)

    @patch('news.services.EenWInstallatieTechniekNews_extract')
    @patch('news.services.WeiiNews_extract')
    @patch('news.services.InstallatieNews_extract')
    def test_update_continues_after_a_source_fails_and_reports_failure(
        self,
        installatie_scraper,
        weii_scraper,
        ew_scraper,
    ):
        installatie_scraper.side_effect = RuntimeError('source unavailable')

        with self.assertRaises(NewsUpdateError):
            update_news()

        weii_scraper.assert_called_once_with(None)
        ew_scraper.assert_called_once_with(None)

    @patch('news.management.commands.update_news.update_news')
    def test_management_command_reports_success(self, update_mock):
        output = StringIO()

        call_command('update_news', stdout=output)

        update_mock.assert_called_once_with()
        self.assertIn('News update completed.', output.getvalue())

    @patch('news.management.commands.update_news.update_news')
    def test_management_command_fails_when_a_source_fails(self, update_mock):
        update_mock.side_effect = NewsUpdateError('Installatie.nl')

        with self.assertRaises(CommandError):
            call_command('update_news', stdout=StringIO())
