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
from apps.habits import views

urlpatterns = [
    path("admin/", admin.site.urls),

    # 首页暂时指向 dashboard
    path("", views.main_dashboard, name="home"),

    # 认证
    path("login/", views.login_page, name="login"),
    path("register/", views.register_page, name="register"),
    path("logout/", views.logout_view, name="logout"),

    # 主要页面
    path("dashboard/", views.main_dashboard, name="main_dashboard"),
    path("history/", views.history_page, name="habit_history"),
    path("recommend/", views.recommend_view, name="recommend"),

    # 创建页面
    path("create/", views.create_page, name="create_page"),

    # 保存习惯
    path("recommend/save/", views.save_habit, name="save_habit"),

    # 习惯相关
    path("my-habits/", views.my_habits, name="my_habits"),
    path("check-in/<int:habit_id>/", views.check_in, name="check_in"),
    path("delete/<int:habit_id>/", views.delete_habit, name="delete_habit"),
    path("adjust/<int:habit_id>/<str:action>/", views.adjust_intensity, name="adjust_intensity"),
    path("calendar/<int:habit_id>/", views.habit_calendar, name="habit_calendar"),
    path("checkin/<int:habit_id>/", views.checkin_date, name="checkin_date"),
    path('recommend/generate/', views.generate_plan, name='generate_plan'),
]
