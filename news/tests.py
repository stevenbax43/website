from io import StringIO
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

import pytz
from django.core.management import call_command, CommandError
from django.test import SimpleTestCase

from .news_scrape import EenWInstallatieTechniekNews_extract, InstallatieNews_extract
from .services import NewsUpdateError, update_news


class NewsUpdateTests(SimpleTestCase):
    @patch('news.news_scrape.requests.get')
    def test_installatie_scraper_reports_a_page_without_articles(self, request_get):
        request_get.return_value = SimpleNamespace(
            status_code=200,
            text='<html><title>Bot Verification</title></html>',
        )

        with self.assertRaisesRegex(RuntimeError, 'returned no news articles'):
            InstallatieNews_extract()

    def test_ew_scraper_parses_dates_without_a_year_and_tolerates_invalid_dates(self):
        listing_html = (
            '<div class="pages-overview"><article class="item page-1">'
            '<div class="caption"><h3>Test article</h3>'
            '<a href="/test-article"></a></div></article></div>'
        )

        cases = (
            ('<span class="edition">17 november</span>', '17 november', (17, 11)),
            ('<span class="edition">31 foo 2026</span>', '31 foo 2026', None),
            ('', '', None),
        )
        for date_markup, expected_text, expected_day_month in cases:
            with self.subTest(date_markup=date_markup):
                article_html = (
                    '<main>{}<figure><img src="/image.jpg"></figure></main>'
                ).format(date_markup)
                responses = (
                    SimpleNamespace(status_code=200, text=listing_html),
                    SimpleNamespace(status_code=200, text=article_html),
                    SimpleNamespace(status_code=200, content=b'image'),
                )
                with patch(
                    'news.news_scrape.requests.get', side_effect=responses
                ), patch('news.news_scrape.NewsArticle') as article_model:
                    article_model.objects.filter.return_value.first.return_value = None

                    EenWInstallatieTechniekNews_extract()

                article_model.assert_called_once()
                self.assertEqual(
                    article_model.call_args.kwargs['date_published_text'],
                    expected_text,
                )
                published_date = article_model.call_args.kwargs[
                    'date_published_datetime'
                ]
                if expected_day_month:
                    self.assertEqual(
                        (published_date.day, published_date.month),
                        expected_day_month,
                    )
                    self.assertEqual(
                        published_date.year,
                        datetime.now(pytz.timezone('Europe/Amsterdam')).year,
                    )
                else:
                    self.assertIsNone(published_date)

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
