from django.db import models
from django.contrib.auth.models import User

class UserHabit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sport_name = models.CharField(max_length=100)
    intensity_level = models.IntegerField(default=1)
    duration_each_time = models.IntegerField(default=30)  # minutes

    experience_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    streak = models.IntegerField(default=0)
    last_checkin = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def required_xp(self):
        return self.level * self.level * 100

    def __str__(self):
        return f"{self.user.username} - {self.sport_name}"


class HabitCheckIn(models.Model):
    user_habit = models.ForeignKey(UserHabit, on_delete=models.CASCADE)
    date = models.DateField()
    xp_gained = models.IntegerField()

    class Meta:
        unique_together = ('user_habit', 'date')

    def __str__(self):
        return f"{self.user_habit.sport_name} - {self.date}"