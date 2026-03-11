from django.test import TestCase
from django.urls import reverse


# Tests for authentication-related views
class AuthViewTests(TestCase):
    # Basic tests for login and password reset pages.

    def test_login_page_status_code(self):
        # Login page should be accessible.
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_login_page_visual_elements(self):
        # Page should contain brand text and CSRF token.
        response = self.client.get(reverse("login"))
        self.assertContains(response, "Habit Tracker")
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_login_logic_redirection(self):
        # Submitting empty login form should not authenticate.
        response = self.client.post(reverse("login"), {})
        # Django usually re-renders the page when form is invalid
        self.assertEqual(response.status_code, 200)

    def test_password_reset_page(self):
        # Password reset page should load correctly.
        response = self.client.get(reverse("password_reset"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reset Password")

    def test_password_reset_flow(self):
        # User should be able to reset password and log in with the new one.

        # create a dummy user
        from django.contrib.auth.models import User
        user = User.objects.create_user(username="foo@example.com", email="foo@example.com", password="oldpass")

        response = self.client.post(reverse("password_reset"), {
            "email": "foo@example.com",
            "password": "newpass",
        })

        # should redirect to dashboard
        self.assertRedirects(response, reverse("main_dashboard"))

        # logging out and trying to login with new password should work
        self.client.logout()
        login = self.client.login(username="foo@example.com", password="newpass")
        self.assertTrue(login)