from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core import mail
from django.test import RequestFactory, TestCase, override_settings
from django.contrib.auth.signals import user_logged_in
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import LoginActivity


class LoginActivityTrackingTests(TestCase):
    def setUp(self):
        self.request = RequestFactory().get(
            "/accounts/login/",
            HTTP_USER_AGENT="Mozilla/5.0",
            REMOTE_ADDR="192.0.2.1",
        )

    def test_owner_is_not_logged_by_username_or_email(self):
        excluded_users = [
            User.objects.create_user(username="stevenbax", email="owner@example.com"),
            User.objects.create_user(
                username="owner-email-user",
                email="steven.bax@kropman.nl",
            ),
        ]

        for user in excluded_users:
            with self.subTest(username=user.username):
                user_logged_in.send(
                    sender=User,
                    request=self.request,
                    user=user,
                )

        self.assertFalse(LoginActivity.objects.exists())

    def test_other_authenticated_users_are_still_logged(self):
        user = User.objects.create_user(
            username="regular-login-user",
            email="user@example.com",
        )

        user_logged_in.send(sender=User, request=self.request, user=user)

        activity = LoginActivity.objects.get()
        self.assertEqual(activity.user, user)
        self.assertTrue(activity.success)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='password-reset-user',
            email='user@example.com',
            password='Old-password-123',
        )

    def test_registered_email_receives_reset_link(self):
        with self.assertLogs('accounts.email', level='INFO') as logs:
            response = self.client.post(
                '/accounts/password-reset/',
                {'email': self.user.email},
            )

        self.assertRedirects(response, '/accounts/password-reset/done/')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/accounts/password-reset/', mail.outbox[0].body)
        self.assertIn('Kropman', mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].alternatives[0][1], 'text/html')
        self.assertIn('O&amp;T-team van Kropman', mail.outbox[0].alternatives[0][0])
        self.assertIn('eligible_accounts=1', logs.output[0])
        self.assertNotIn(self.user.email, '\n'.join(logs.output))

    def test_unregistered_email_gets_same_confirmation_without_email(self):
        with self.assertLogs('accounts.email', level='INFO') as logs:
            response = self.client.post(
                '/accounts/password-reset/',
                {'email': 'unknown@example.com'},
            )

        self.assertRedirects(response, '/accounts/password-reset/done/')
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn('eligible_accounts=0', logs.output[0])

    def test_valid_reset_link_changes_password(self):
        reset_url = (
            f'/accounts/password-reset/'
            f'{urlsafe_base64_encode(force_bytes(self.user.pk))}/'
            f'{default_token_generator.make_token(self.user)}/'
        )
        response = self.client.get(reset_url)
        self.assertRedirects(
            response,
            f'/accounts/password-reset/'
            f'{urlsafe_base64_encode(force_bytes(self.user.pk))}/set-password/',
        )

        response = self.client.post(
            response.url,
            {
                'new_password1': 'New-password-456',
                'new_password2': 'New-password-456',
            },
        )

        self.assertRedirects(response, '/accounts/password-reset/complete/')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('New-password-456'))
