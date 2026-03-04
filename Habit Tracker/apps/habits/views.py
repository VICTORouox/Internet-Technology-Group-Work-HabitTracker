from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import UserHabit
import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.utils import timezone
from .models import HabitCheckIn

def register_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Check if the email address already exists.
        if User.objects.filter(username=email).exists():
            return render(request, 'auth/register.html', {'error': 'This email has been registered.'})
        
        # Create user
        user = User.objects.create_user(username=email, email=email, password=password)
        user.save()
        
        # Log in directly after successful registration and be redirected.
        auth_login(request, user)
        return redirect('main_dashboard')
        
    return render(request, 'auth/register.html')


def password_reset_page(request):
    """Simple student-style password reset.

    Users submit their email along with a new password. If the account
    exists we overwrite its password and log them in.  The frontend already
    verifies that the two passwords match.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            return render(request, 'auth/password_reset.html', {'error': 'No account found for that email.'})

        user.set_password(password)
        user.save()

        # automatically log the user in after resetting
        auth_login(request, user)
        return redirect('main_dashboard')

    return render(request, 'auth/password_reset.html')

def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('main_dashboard')
        else:
            return render(request, 'auth/login.html', {'error': 'Invalid email or password.'})
            
    return render(request, 'auth/login.html')

def main_dashboard(request):
    return render(request, 'habits/dashboard.html')

def logout_view(request):
    auth_logout(request)
    return redirect('login')

def history_page(request):
    return render(request, 'habits/history.html')

# =========================
# Sport dataset
# =========================
SPORT_LIBRARY = {

    "Running": {
        "icon": "🏃",
        "type": "Endurance",
        "plan": "30 mins / session",
        "upgrade": "Increase distance by 10% weekly.",
        "image": "images/running.jpg"
    },

    "Cycling": {
        "icon": "🚴",
        "type": "Cardio",
        "plan": "45 mins / session",
        "upgrade": "Add uphill routes.",
        "image": "images/cycling.jpg"
    },

    "Swimming": {
        "icon": "🏊",
        "type": "Full Body",
        "plan": "40 mins / session",
        "upgrade": "Reduce rest time gradually.",
        "image": "images/swimming.jpg"
    },

    "Yoga": {
        "icon": "🧘",
        "type": "Flexibility",
        "plan": "30 mins / session",
        "upgrade": "Try advanced poses.",
        "image": "images/yoga.jpg"
    },

    "Rope Skipping": {
        "icon": "🪢",
        "type": "Fat Burning",
        "plan": "20 mins / session",
        "upgrade": "Increase interval intensity.",
        "image": "images/ropeskipping.jpg"
    },

    "Strength Training": {
        "icon": "🏋️",
        "type": "Muscle Building",
        "plan": "45 mins / session",
        "upgrade": "Progressively increase weights.",
        "image": "images/strength.jpg"
    },

    "HIIT": {
        "icon": "🔥",
        "type": "High Intensity",
        "plan": "20–30 mins / session",
        "upgrade": "Increase interval intensity.",
        "image": "images/hiit.jpg"
    },

    "Brisk Walking": {
        "icon": "🚶",
        "type": "Low Impact",
        "plan": "30 mins / session",
        "upgrade": "Increase pace gradually.",
        "image": "images/walking.jpg"
    }
}
# =========================
# Recommendation arithmetic
# =========================
def recommendation_engine(data):
    goal = data.get("goal")
    preference = data.get("preference")
    height = float(data.get("height"))
    weight = float(data.get("weight"))
    conditions = data.getlist("conditions") if hasattr(data, "getlist") else data.get("conditions", [])

    # 计算 BMI
    bmi = weight / ((height / 100) ** 2)

    # 初始分
    scores = {sport: 50 for sport in SPORT_LIBRARY.keys()}

    # ========================
    # 1️⃣ 根据目标加权
    # ========================

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

    # ========================
    # 2️⃣ 偏好加权
    # ========================

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

    # ========================
    # 3️⃣ BMI 判断
    # ========================

    if bmi < 18.5:
        scores["Strength Training"] += 20
        scores["Yoga"] += 10

    elif 18.5 <= bmi < 24:
        scores["Running"] += 10
        scores["Cycling"] += 10

    elif 24 <= bmi < 28:
        scores["Running"] += 15
        scores["Swimming"] += 15

    else:  # BMI >= 28
        scores["Brisk Walking"] += 40
        scores["Swimming"] += 30
        scores["Running"] -= 20
        scores["Rope Skipping"] -= 25

    # ========================
    # 4️⃣ 伤病条件判断
    # ========================

    if isinstance(conditions, list):
        if "Weak knees" in conditions:
            scores["Running"] -= 40
            scores["Rope Skipping"] -= 40
            scores["Cycling"] += 15

        if "Lower back pain" in conditions:
            scores["Strength Training"] -= 20
            scores["Yoga"] += 15

        if "Asthma" in conditions:
            scores["HIIT"] -= 25
            scores["Swimming"] += 20

    # ========================
    # 5️⃣ 排序选前三
    # ========================

    sorted_sports = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top3 = sorted_sports[:3]

    candidates = []

    for name, score in top3:
        sport = SPORT_LIBRARY[name]
        candidates.append({
            "name": name,
            "icon": sport["icon"],
            "type": sport["type"],
            "match": min(score, 99),
            "reason": f"Optimized based on your goal, BMI ({round(bmi,1)}), preference, and physical condition.",
            "plan": sport["plan"],
            "upgrade": sport["upgrade"]
        })

    return candidates

# =========================
# Page logic
# =========================
def recommend_view(request):
    return render(request, 'habits/recommend.html')

def generate_plan(request):
    if request.method == "POST":
        candidates = recommendation_engine(request.POST)

        return render(request, "habits/recommend_result.html", {
            "candidates": candidates
        })

@login_required
def save_habit(request):
    if request.method == "POST":

        habit_name = request.POST.get("habit_name")
        duration = request.POST.get("duration")
        force_create = request.POST.get("force_create")

        duration_minutes = int(duration.split()[0])

        # 检查是否已存在
        exists = UserHabit.objects.filter(
            user=request.user,
            sport_name=habit_name
        ).exists()

        # 如果已存在且不是强制创建
        if exists and not force_create:
            return render(request, "habits/create.html", {
                "sports": SPORT_LIBRARY,
                "duplicate": True,
                "duplicate_name": habit_name
            })

        # 正常创建
        UserHabit.objects.create(
            user=request.user,
            sport_name=custom_name,
            sport_type=sport_type,
            duration_each_time=duration_minutes,
            intensity_level=1
        )

        return redirect("my_habits")
    
@login_required
def my_habits(request):
    habits = UserHabit.objects.filter(user=request.user)

    for habit in habits:
        if habit.required_xp() > 0:
            percentage = (habit.experience_points / habit.required_xp()) * 100
            habit.xp_percentage = int(percentage)
        else:
            habit.xp_percentage = 0

    return render(request, "habits/my_habits.html", {"habits": habits})

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

    if habit.last_checkin == today - timezone.timedelta(days=1):
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

    if action == "decrease" and habit.intensity_level > 1:
        habit.intensity_level -= 1
        habit.duration_each_time -= 10

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
        "checkins": calendar_data,
        "habit_id": habit.id,
        "xp_per_check": habit.intensity_level * 10
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
def create_page(request):
    return render(request, "habits/create.html", {
        "sports": SPORT_LIBRARY
    })