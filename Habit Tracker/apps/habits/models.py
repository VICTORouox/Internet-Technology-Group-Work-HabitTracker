from django.db import models
from django.contrib.auth.models import User


# =====================================================
# User Habit Model
# Stores a user's exercise habit configuration
# =====================================================

class UserHabit(models.Model):

    # Owner of the habit
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Custom habit name created by user
    habit_name = models.CharField(max_length=100, blank=True)

    # Sport category
    sport_type = models.CharField(max_length=50)

    # Training intensity level (1–5)
    intensity_level = models.IntegerField(default=1)

    # Duration of each session (minutes)
    duration_each_time = models.IntegerField(default=30)

    # XP system for gamification
    experience_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)

    # Consecutive check-in days
    streak = models.IntegerField(default=0)

    # Last check-in date
    last_checkin = models.DateField(null=True, blank=True)

    # Record creation time
    created_at = models.DateTimeField(auto_now_add=True)

    def required_xp(self):
        """XP required to reach the next level."""
        return self.level * self.level * 100

    def display_name(self):
        """
        Display name used in UI.

        Examples:
        Morning (Running)
        Running
        """
        if self.habit_name:
            return f"{self.habit_name} ({self.sport_type})"
        return self.sport_type

    def __str__(self):
        """Readable representation in Django admin."""
        return f"{self.user.username} - {self.display_name()}"


# =====================================================
# Habit Check-in Model
# Records each completed exercise session
# =====================================================

class HabitCheckIn(models.Model):

    # Related habit
    user_habit = models.ForeignKey(UserHabit, on_delete=models.CASCADE)

    # Date of the check-in
    date = models.DateField()

    # XP earned from this session
    xp_gained = models.IntegerField()

    # Duration of the workout session (minutes)
    duration = models.IntegerField()

    class Meta:
        # Prevent duplicate check-ins on the same day
        unique_together = ('user_habit', 'date')

    def __str__(self):
        """Readable record format."""
        return f"{self.user_habit.display_name()} - {self.date} ({self.duration} mins)"