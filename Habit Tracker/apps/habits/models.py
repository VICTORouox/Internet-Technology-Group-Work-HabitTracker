from django.db import models
from django.contrib.auth.models import User


class UserHabit(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # 用户自定义名称，例如：Morning / Cardio / 222
    habit_name = models.CharField(max_length=100, blank=True)

    # 运动类型，例如：Running / Yoga / HIIT
    sport_type = models.CharField(max_length=50)

    intensity_level = models.IntegerField(default=1)
    duration_each_time = models.IntegerField(default=30)  # minutes

    experience_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    streak = models.IntegerField(default=0)

    last_checkin = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def required_xp(self):
        return self.level * self.level * 100

    def display_name(self):
        """
        页面显示名称：
        Morning (Running)
        Running
        """
        if self.habit_name:
            return f"{self.habit_name} ({self.sport_type})"
        return self.sport_type

    def __str__(self):
        return f"{self.user.username} - {self.display_name()}"


class HabitCheckIn(models.Model):
    user_habit = models.ForeignKey(UserHabit, on_delete=models.CASCADE)
    date = models.DateField()
    xp_gained = models.IntegerField()
    duration = models.IntegerField()

    class Meta:
        unique_together = ('user_habit', 'date')

    def __str__(self):
        return f"{self.user_habit.display_name()} - {self.date} ({self.duration} mins)"