from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum
from django.http import JsonResponse
import json

from .models import UserHabit, HabitCheckIn


# =====================================================
# Authentication Views
# Handles user account actions such as register/login
# =====================================================

def register_page(request):
    """
    Render and handle the user registration page.
    Creates a new user and logs them in immediately.
    """

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Prevent duplicate accounts
        if User.objects.filter(username=email).exists():
            return render(request, 'auth/register.html', {
                'error': 'This email has been registered.'
            })

        # Create account
        user = User.objects.create_user(username=email, email=email, password=password)

        # Automatically log in after registration
        auth_login(request, user)

        return redirect('main_dashboard')

    return render(request, 'auth/register.html')


def password_reset_page(request):
    """
    Allows a user to reset their password by entering email and new password.
    """

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
    """
    Handle user login authentication.
    """

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
    """
    Log the current user out and redirect to login page.
    """

    auth_logout(request)
    return redirect('login')


def main_dashboard(request):
    """
    Main dashboard page after login.
    """

    return render(request, 'habits/dashboard.html')


def history_page(request):
    """
    Display historical habit activity page.
    """

    return render(request, 'habits/history.html')


# =====================================================
# Sport Dataset
# Static dataset used by the recommendation system
# =====================================================

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


# =====================================================
# Recommendation Engine
# Core algorithm used to suggest sports habits
# =====================================================

def recommendation_engine(data):
    """
    Generate sport recommendations based on:
    - User goal
    - Exercise preference
    - BMI
    - Health conditions
    """

    goal = data.get("goal")
    preference = data.get("preference")

    height = float(data.get("height"))
    weight = float(data.get("weight"))

    conditions = data.getlist("conditions") if hasattr(data, "getlist") else []

    # BMI calculation
    bmi = weight / ((height / 100) ** 2)

    # Base score for all sports
    scores = {sport: 50 for sport in SPORT_LIBRARY}

    # Goal based scoring
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

    # Preference scoring
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

    # BMI adjustments
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

    # Sort by score and select top 3
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


# =====================================================
# Recommendation Pages
# UI pages that interact with the recommendation engine
# =====================================================

def recommend_view(request):
    """
    Display the recommendation questionnaire page.
    """

    return render(request, 'habits/recommend.html')


def generate_plan(request):
    """
    Process questionnaire results and generate sport recommendations.
    """

    if request.method == "POST":

        candidates = recommendation_engine(request.POST)

        # Store query in session for later reuse
        request.session['recommendation_query'] = request.POST.urlencode()

        return render(request, "habits/recommend_result.html", {
            "candidates": json.dumps(candidates)
        })


# =====================================================
# Habit Creation
# Handles creation of habits from manual input or recommendation
# =====================================================

@login_required
def save_habit(request):

    if request.method == "POST":

        habit_name = (request.POST.get("habit_name") or "").strip()
        sport_type = (request.POST.get("sport_type") or "").strip()

        duration = request.POST.get("duration")
        duration_minutes = int(duration.split()[0])

        from_recommend = request.POST.get("from_recommend")

        # If created directly from recommendation system
        if from_recommend == "true":

            UserHabit.objects.create(
                user=request.user,
                habit_name="",
                sport_type=sport_type,
                duration_each_time=duration_minutes,
                intensity_level=1
            )

            return redirect("my_habits")

        # Check for duplicate habit name + type
        name_exists = UserHabit.objects.filter(
            user=request.user,
            habit_name=habit_name,
            sport_type=sport_type
        ).exists()

        if name_exists:

            if request.POST.get("from_recommend_page") == "true":

                from django.http import QueryDict
                query = request.session.get('recommendation_query', '')

                candidates = recommendation_engine(QueryDict(query))

                return render(request, "habits/recommend_result.html", {
                    "candidates": candidates,
                    "error": "You already have a habit with this name and sport type. This combination cannot be created again.",
                    "error_type": "duplicate_exact"
                })

            return render(request, "habits/create.html", {
                "duplicate": True,
                "duplicate_type": "name"
            })

        UserHabit.objects.create(
            user=request.user,
            habit_name=habit_name,
            sport_type=sport_type,
            duration_each_time=duration_minutes,
            intensity_level=1
        )

        return redirect("/my-habits/?created=1")

    return redirect("create_page")


# =====================================================
# Habit Management Pages
# Display and manage user habits
# =====================================================

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


# =====================================================
# Habit Check-in System
# Handles daily habit tracking and XP system
# =====================================================

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
        xp_gained=xp_gained,
        duration=habit.duration_each_time
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
            xp_gained=xp_gain,
            duration=habit.duration_each_time
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


# =====================================================
# Habit Creation Page
# =====================================================

@login_required
def create_page(request):

    return render(request, "habits/create.html", {
        "sports": SPORT_LIBRARY
    })


# =====================================================
# Habit Data Analysis
# Provides monthly/yearly statistics for charts
# =====================================================

@login_required
def habit_analysis(request, habit_id):

    habit = get_object_or_404(UserHabit, id=habit_id, user=request.user)

    view = request.GET.get("view", "monthly")

    month_param = request.GET.get("month")

    current_year = datetime.now().year

    if month_param is not None:
        month_param = int(month_param) + 1

    if view == "monthly":

        if month_param:

            from calendar import monthrange

            days_in_month = monthrange(current_year, month_param)[1]

            daily_data = [
                sum(c.duration for c in HabitCheckIn.objects.filter(
                    user_habit=habit,
                    date__year=current_year,
                    date__month=month_param,
                    date__day=day
                )) for day in range(1, days_in_month + 1)
            ]

            return JsonResponse({
                "labels": [str(d) for d in range(1, days_in_month + 1)],
                "data": daily_data
            })

        monthly_data = [
            sum(c.duration for c in HabitCheckIn.objects.filter(
                user_habit=habit,
                date__year=current_year,
                date__month=m
            )) for m in range(1,13)
        ]

        return JsonResponse({
            "labels": [str(m) for m in range(1,13)],
            "data": monthly_data
        })

    elif view == "yearly":

        monthly_data = [
            sum(c.duration for c in HabitCheckIn.objects.filter(
                user_habit=habit,
                date__year=current_year,
                date__month=m
            )) for m in range(1,13)
        ]

        return JsonResponse({
            "labels": [str(m) for m in range(1,13)],
            "data": monthly_data
        })