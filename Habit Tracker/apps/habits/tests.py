from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import json

from .models import UserHabit, HabitCheckIn


# ==============================
# Authentication Tests
# ==============================

class AuthTests(TestCase):

    def test_login_page_load(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_register_page_load(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_user_registration(self):
        response = self.client.post(reverse("register"), {
            "email": "test@example.com",
            "password": "test123"
        })

        self.assertTrue(User.objects.filter(username="test@example.com").exists())
        self.assertRedirects(response, reverse("main_dashboard"))

    def test_login_function(self):
        User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="test123"
        )

        response = self.client.post(reverse("login"), {
            "email": "test@example.com",
            "password": "test123"
        })

        self.assertRedirects(response, reverse("main_dashboard"))

    def test_password_reset(self):
        User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="oldpass"
        )

        response = self.client.post(reverse("password_reset"), {
            "email": "test@example.com",
            "password": "newpass"
        })

        self.assertRedirects(response, reverse("main_dashboard"))


# ==============================
# Habit Model Tests
# ==============================

class HabitModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="user@test.com",
            password="test123"
        )

    def test_required_xp_calculation(self):
        habit = UserHabit.objects.create(
            user=self.user,
            sport_type="Running",
            level=2
        )

        self.assertEqual(habit.required_xp(), 400)

    def test_display_name(self):
        habit = UserHabit.objects.create(
            user=self.user,
            habit_name="Morning",
            sport_type="Running"
        )

        self.assertEqual(habit.display_name(), "Morning (Running)")

    def test_display_name_without_custom_name(self):
        habit = UserHabit.objects.create(
            user=self.user,
            sport_type="Running"
        )

        self.assertEqual(habit.display_name(), "Running")


# ==============================
# Habit Management Tests
# ==============================

class HabitViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="user@test.com",
            password="test123"
        )

        self.client.login(username="user@test.com", password="test123")

        self.habit = UserHabit.objects.create(
            user=self.user,
            sport_type="Running",
            duration_each_time=30,
            intensity_level=1
        )

    def test_my_habits_page(self):
        response = self.client.get(reverse("my_habits"))
        self.assertEqual(response.status_code, 200)

    def test_delete_habit(self):
        habit_id = self.habit.id

        response = self.client.get(
            reverse("delete_habit", args=[habit_id])
        )

        self.assertFalse(UserHabit.objects.filter(id=habit_id).exists())

    def test_adjust_intensity_increase(self):

        response = self.client.get(
            reverse("adjust_intensity", args=[self.habit.id, "increase"])
        )

        self.habit.refresh_from_db()

        self.assertEqual(self.habit.intensity_level, 2)

    def test_adjust_intensity_decrease(self):

        self.habit.intensity_level = 3
        self.habit.save()

        response = self.client.get(
            reverse("adjust_intensity", args=[self.habit.id, "decrease"])
        )

        self.habit.refresh_from_db()

        self.assertEqual(self.habit.intensity_level, 2)


# ==============================
# Check-in System Tests
# ==============================

class CheckinTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="user@test.com",
            password="test123"
        )

        self.client.login(username="user@test.com", password="test123")

        self.habit = UserHabit.objects.create(
            user=self.user,
            sport_type="Running",
            intensity_level=2,
            duration_each_time=30
        )

    def test_checkin_creates_record(self):

        response = self.client.get(
            reverse("check_in", args=[self.habit.id])
        )

        self.assertTrue(
            HabitCheckIn.objects.filter(user_habit=self.habit).exists()
        )

    def test_duplicate_checkin_prevention(self):

        today = timezone.now().date()

        HabitCheckIn.objects.create(
            user_habit=self.habit,
            date=today,
            xp_gained=10,
            duration=30
        )

        response = self.client.get(
            reverse("check_in", args=[self.habit.id])
        )

        self.assertEqual(
            HabitCheckIn.objects.filter(user_habit=self.habit).count(),
            1
        )


# ==============================
# API Tests
# ==============================

class APITests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="user@test.com",
            password="test123"
        )

        self.client.login(username="user@test.com", password="test123")

        self.habit = UserHabit.objects.create(
            user=self.user,
            sport_type="Running",
            duration_each_time=30,
            intensity_level=1
        )

    def test_calendar_api(self):

        response = self.client.get(
            reverse("habit_calendar", args=[self.habit.id])
        )

        self.assertEqual(response.status_code, 200)

    def test_checkin_api(self):

        today = timezone.now().date().strftime("%Y-%m-%d")

        response = self.client.post(
            reverse("checkin_date", args=[self.habit.id]),
            json.dumps({"date": today}),
            content_type="application/json"
        )

        data = json.loads(response.content)

        self.assertEqual(data["status"], "success")

    def test_analysis_api(self):

        response = self.client.get(
            reverse("habit_analysis", args=[self.habit.id])
        )

        self.assertEqual(response.status_code, 200)