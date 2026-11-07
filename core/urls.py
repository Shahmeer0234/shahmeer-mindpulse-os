from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('tasks/', views.tasks_view, name='tasks'),
    path('videos/', views.videos_view, name='videos'),
    path('neural-quests/', views.neural_quests_view, name='neural_quests'),
    path('task/toggle/<int:task_id>/', views.toggle_task, name='toggle_task'),
    path('task/delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('api/save-session/', views.save_session_data, name='save_session'),
    
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
]