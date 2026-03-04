"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from apps.habits.views import login_page, register_page, history_page, main_dashboard, logout_view, recommend_view, password_reset_page
from apps.habits import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('login/', login_page, name='login'),
    path('history/', history_page, name='habit_history'),
    path('register/', register_page, name='register'),
    path('password-reset/', password_reset_page, name='password_reset'),
    path('dashboard/', main_dashboard, name='main_dashboard'),
    path('logout/', logout_view, name='logout'),
    path('recommend/', recommend_view, name='recommend'),
    path('recommend/generate/', views.generate_plan, name='generate_plan'),
    path('recommend/save/', views.save_habit, name='save_habit'),
    path("my-habits/", views.my_habits, name="my_habits"),
    path("check-in/<int:habit_id>/", views.check_in, name="check_in"),
    path("delete/<int:habit_id>/", views.delete_habit, name="delete_habit"),
    path("adjust/<int:habit_id>/<str:action>/", views.adjust_intensity, name="adjust_intensity"),
    path("calendar/<int:habit_id>/", views.habit_calendar, name="habit_calendar"),
    path("checkin/<int:habit_id>/", views.checkin_date, name="checkin_date"),
]
