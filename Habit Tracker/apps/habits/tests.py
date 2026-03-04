from django.test import TestCase
from django.urls import reverse


class AuthViewTests(TestCase):
    """验证身份验证页面的核心功能"""

    def test_login_page_status_code(self):
        """测试登录页面是否能正常访问"""
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_login_page_visual_elements(self):
        """测试页面是否包含必要的品牌元素和 CSRF 令牌"""
        response = self.client.get(reverse("login"))
        self.assertContains(response, "Habit Tracker")
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_login_logic_redirection(self):
        """测试空数据提交是否被拦截（或返回错误）"""
        response = self.client.post(reverse("login"), {})
        # Django 默认会在表单无效时重新渲染当前页
        self.assertEqual(response.status_code, 200)

    def test_password_reset_page(self):
        """页面应该可以访问并包含正确的标题"""
        response = self.client.get(reverse("password_reset"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reset Password")

    def test_password_reset_flow(self):
        """重置密码后用户应被自动登录并重定向"""
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
