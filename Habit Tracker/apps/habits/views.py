from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import UserHabit, HabitCheckIn


# =========================
# Auth
# =========================

def register_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=email).exists():
            return render(request, 'auth/register.html', {
                'error': 'This email has been registered.'
            })

        user = User.objects.create_user(username=email, email=email, password=password)
        auth_login(request, user)
        return redirect('main_dashboard')

    return render(request, 'auth/register.html')


def password_reset_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            return render(request, 'auth/password_reset.html', {
                'error': 'No account found for that email.'
            })

        user.set_password(password)
        user.save()

        auth_login(request, user)
        return redirect('main_dashboard')

    return render(request, 'auth/password_reset.html')


def login_page(request):
    if request.method == 'POST':

        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user:
            auth_login(request, user)
            return redirect('main_dashboard')

        return render(request, 'auth/login.html', {
            'error': 'Invalid email or password.'
        })

    return render(request, 'auth/login.html')


def logout_view(request):
    auth_logout(request)
    return redirect('login')


def main_dashboard(request):
    return render(request, 'habits/dashboard.html')


def history_page(request):
    return render(request, 'habits/history.html')


# =========================
# Sport dataset
# =========================

SPORT_LIBRARY = {

    "Running": {
        "icon": "🏃",
        "type": "Cardio",
        "plan": "30 mins / session",
        "upgrade": "Increase distance by 10% weekly.",
    },

    "Cycling": {
        "icon": "🚴",
        "type": "Cardio",
        "plan": "45 mins / session",
        "upgrade": "Add uphill routes.",
    },

    "Swimming": {
        "icon": "🏊",
        "type": "Cardio",
        "plan": "40 mins / session",
        "upgrade": "Reduce rest time gradually.",
    },

    "Yoga": {
        "icon": "🧘",
        "type": "Flexibility",
        "plan": "30 mins / session",
        "upgrade": "Try advanced poses.",
    },

    "Rope Skipping": {
        "icon": "🪢",
        "type": "Fat Burning",
        "plan": "20 mins / session",
        "upgrade": "Increase interval intensity.",
    },

    "Strength Training": {
        "icon": "🏋️",
        "type": "Strength",
        "plan": "45 mins / session",
        "upgrade": "Progressively increase weights.",
    },

    "HIIT": {
        "icon": "🔥",
        "type": "Fat Burning",
        "plan": "20–30 mins / session",
        "upgrade": "Increase interval intensity.",
    },

    "Brisk Walking": {
        "icon": "🚶",
        "type": "Low Impact",
        "plan": "30 mins / session",
        "upgrade": "Increase pace gradually.",
    }
}


# =========================
# Recommendation Engine
# =========================

def recommendation_engine(data):

    goal = data.get("goal")
    preference = data.get("preference")

    height = float(data.get("height"))
    weight = float(data.get("weight"))

    conditions = data.getlist("conditions") if hasattr(data, "getlist") else []

    bmi = weight / ((height / 100) ** 2)

    scores = {sport: 50 for sport in SPORT_LIBRARY}

    if goal == "Improve physical fitness":
        scores["Running"] += 25
        scores["Cycling"] += 20
        scores["Swimming"] += 15

    elif goal == "Fat loss and body shaping":
        scores["Rope Skipping"] += 30
        scores["Running"] += 20
        scores["HIIT"] += 25

    elif goal == "Relieve stress":
        scores["Yoga"] += 35
        scores["Swimming"] += 20

    elif goal == "Build muscle":
        scores["Strength Training"] += 40
        scores["HIIT"] += 20

    if preference == "cardio":
        scores["Running"] += 15
        scores["Cycling"] += 15
        scores["Swimming"] += 15

    elif preference == "strength":
        scores["Strength Training"] += 25
        scores["HIIT"] += 15

    elif preference == "flexibility":
        scores["Yoga"] += 30

    elif preference == "outdoor":
        scores["Running"] += 10
        scores["Cycling"] += 10

    if bmi < 18.5:
        scores["Strength Training"] += 20

    elif 18.5 <= bmi < 24:
        scores["Running"] += 10
        scores["Cycling"] += 10

    elif 24 <= bmi < 28:
        scores["Running"] += 15
        scores["Swimming"] += 15

    else:
        scores["Brisk Walking"] += 40
        scores["Swimming"] += 30
        scores["Running"] -= 20

    sorted_sports = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]

    candidates = []

    for name, score in sorted_sports:
        sport = SPORT_LIBRARY[name]

        candidates.append({
            "name": name,
            "icon": sport["icon"],
            "type": sport["type"],
            "match": min(score, 99),
            "reason": f"Optimized based on your goal, BMI ({round(bmi,1)}).",
            "plan": sport["plan"],
            "upgrade": sport["upgrade"]
        })

    return candidates


# =========================
# Recommendation pages
# =========================

def recommend_view(request):
    return render(request, 'habits/recommend.html')


def generate_plan(request):

    if request.method == "POST":

        candidates = recommendation_engine(request.POST)

        return render(request, "habits/recommend_result.html", {
            "candidates": candidates
        })


# =========================
# Habit creation
# =========================

@login_required
def save_habit(request):

    if request.method == "POST":

        habit_name = (request.POST.get("habit_name") or "").strip()
        sport_type = (request.POST.get("sport_type") or "").strip()

        duration = request.POST.get("duration")
        duration_minutes = int(duration.split()[0])

        from_recommend = request.POST.get("from_recommend")
        force_create = request.POST.get("force_create")

        # 推荐创建：跳过重复检测
        if from_recommend == "true":

            UserHabit.objects.create(
                user=request.user,
                habit_name="",
                sport_type=sport_type,
                duration_each_time=duration_minutes,
                intensity_level=1
            )

            return redirect("my_habits")

        # 同名同运动检测
        name_exists = UserHabit.objects.filter(
            user=request.user,
            habit_name=habit_name,
            sport_type=sport_type
        ).exists()

        # 是否已有该运动
        sport_exists = UserHabit.objects.filter(
            user=request.user,
            sport_type=sport_type
        ).exists()

        if force_create != "true":

            if name_exists:
                return render(request, "habits/create.html", {
                    "duplicate": True,
                    "duplicate_type": "name"
                })

            if sport_exists:
                return render(request, "habits/create.html", {
                    "duplicate": True,
                    "duplicate_type": "sport"
                })

        UserHabit.objects.create(
            user=request.user,
            habit_name=habit_name,
            sport_type=sport_type,
            duration_each_time=duration_minutes,
            intensity_level=1
        )

        return redirect("my_habits")

    return redirect("create_page")


# =========================
# Habit pages
# =========================

@login_required
def my_habits(request):

    habits = UserHabit.objects.filter(user=request.user)

    for habit in habits:

        xp_required = habit.required_xp()

        habit.xp_percentage = int(
            (habit.experience_points / xp_required) * 100
        ) if xp_required else 0

    return render(request, "habits/my_habits.html", {"habits": habits})


@login_required
def delete_habit(request, habit_id):

    habit = get_object_or_404(UserHabit, id=habit_id, user=request.user)
    habit.delete()

    return redirect("my_habits")


@login_required
def adjust_intensity(request, habit_id, action):

    habit = get_object_or_404(UserHabit, id=habit_id, user=request.user)

    if action == "increase" and habit.intensity_level < 5:
        habit.intensity_level += 1
        habit.duration_each_time += 10

    elif action == "decrease" and habit.intensity_level > 1:
        habit.intensity_level -= 1
        habit.duration_each_time -= 10

    habit.save()

    return redirect("my_habits")


# =========================
# Check-in system
# =========================

@login_required
def check_in(request, habit_id):

    habit = get_object_or_404(UserHabit, id=habit_id, user=request.user)
    today = timezone.now().date()

    if HabitCheckIn.objects.filter(user_habit=habit, date=today).exists():
        return redirect("my_habits")

    xp_gained = habit.intensity_level * 10

    HabitCheckIn.objects.create(
        user_habit=habit,
        date=today,
        xp_gained=xp_gained
    )

    habit.experience_points += xp_gained

    if habit.last_checkin == today - timedelta(days=1):
        habit.streak += 1
    else:
        habit.streak = 1

    habit.last_checkin = today

    while habit.experience_points >= habit.required_xp():
        habit.experience_points -= habit.required_xp()
        habit.level += 1

    habit.save()

    return redirect("my_habits")


@login_required
def habit_calendar(request, habit_id):

    habit = get_object_or_404(UserHabit, id=habit_id, user=request.user)

    checkins = HabitCheckIn.objects.filter(
        user_habit=habit
    ).values_list("date", flat=True)

    calendar_data = [d.strftime("%Y-%m-%d") for d in checkins]

    return JsonResponse({
        "checkins": calendar_data
    })


@login_required
def checkin_date(request, habit_id):

    if request.method == "POST":

        habit = get_object_or_404(UserHabit, id=habit_id, user=request.user)

        data = json.loads(request.body)
        date_str = data.get("date")

        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

        if HabitCheckIn.objects.filter(user_habit=habit, date=date_obj).exists():
            return JsonResponse({"status": "exists"})

        xp_gain = habit.intensity_level * 10

        HabitCheckIn.objects.create(
            user_habit=habit,
            date=date_obj,
            xp_gained=xp_gain
        )

        habit.experience_points += xp_gain

        if habit.last_checkin == date_obj - timedelta(days=1):
            habit.streak += 1
        else:
            habit.streak = 1

        habit.last_checkin = date_obj

        while habit.experience_points >= habit.required_xp():
            habit.experience_points -= habit.required_xp()
            habit.level += 1

        habit.save()

        return JsonResponse({"status": "success"})


@login_required
def create_page(request):

    return render(request, "habits/create.html", {
        "sports": SPORT_LIBRARY
    })