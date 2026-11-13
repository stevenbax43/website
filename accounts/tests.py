from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.test import RequestFactory, TestCase

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
