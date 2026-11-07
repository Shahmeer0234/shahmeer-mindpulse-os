from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DailyCheckIn, WorkSession, CBTIntervention, MotivationalVideo, Task
from .models import StreakTracker, DailyUserQuest, NeuralQuest
from django.http import JsonResponse
import json
import csv
from .forms import TaskForm, VideoUploadForm
import random
from django.utils import timezone
import datetime

def home_view(request):
    return render(request, 'core/home.html')

@login_required(login_url='/login/')
def dashboard_view(request):
    if request.method == 'POST':
        mood = request.POST.get('starting_mood')
        energy = request.POST.get('energy_level')
        if mood and energy:
            DailyCheckIn.objects.create(
                user=request.user,
                starting_mood=mood,
                energy_level=int(energy)
            )
            return redirect('dashboard')

    user_sessions = WorkSession.objects.filter(user=request.user).order_by('-start_time')[:10]
    total_tasks = Task.objects.filter(user=request.user).count()
    completed_tasks = Task.objects.filter(user=request.user, is_completed=True).count()
    latest_checkin = DailyCheckIn.objects.filter(user=request.user).last()

    session_labels = [s.task_title for s in reversed(user_sessions)]
    fatigue_scores = [s.fatigue_score for s in reversed(user_sessions)]

    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'latest_checkin': latest_checkin,
        'session_labels': session_labels,
        'fatigue_scores': fatigue_scores,
    }
    return render(request, 'core/dashboard.html', context)

@login_required(login_url='/login/')
def tasks_view(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('tasks')
    
    form = TaskForm()
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/tasks.html', {'form': form, 'tasks': tasks})

@login_required(login_url='/login/')
def videos_view(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.user = request.user
            video.save()
            return redirect('videos')
            
    form = VideoUploadForm()
    videos = MotivationalVideo.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'core/videos.html', {'form': form, 'videos': videos})

@login_required(login_url='/login/')
def toggle_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.is_completed = not task.is_completed
    task.save()
    return redirect('tasks')

@login_required(login_url='/admin/login/')
def save_session_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_title = data.get('task_title', 'General Focus Session')
            switches = data.get('context_switches', 0)
            duration = data.get('duration_minutes', 25)
            is_completed = data.get('is_completed', True)

            time_factor = (duration / 60.0) * 50.0
            switch_factor = min(switches * 6.0, 50.0)
            calculated_fatigue = round(min(100.0, time_factor + switch_factor), 2)

            if calculated_fatigue > 60:
                cbt_prompt = "High Cognitive Load Detected: Take a 2-minute Box Breathing break (Inhale for 4s, hold 4s, exhale 4s, hold 4s)."
                trigger = "High Fatigue > 60%"
            elif switches > 3:
                cbt_prompt = "Frequent Context Switching: Practice cognitive reframing. Focus on a single sub-task for the next 15 minutes."
                trigger = "High Context Switches"
            else:
                cbt_prompt = "Great Focus Flow! Do a quick 20-20-20 eye rest rule: Look at something 20 feet away for 20 seconds."
                trigger = "Routine Mental Maintenance"

            session = WorkSession.objects.create(
                user=request.user,
                task_title=task_title,
                duration_minutes=duration,
                context_switches=switches,
                fatigue_score=calculated_fatigue,
                is_completed=is_completed
            )

            CBTIntervention.objects.create(
                user=request.user,
                trigger_reason=trigger,
                prompt_text=cbt_prompt
            )

            sessions = WorkSession.objects.filter(user=request.user).values(
                'id', 'task_title', 'start_time', 'duration_minutes', 
                'fatigue_score', 'context_switches', 'is_completed'
            )
            
            csv_filename = 'worksessions_export.csv'
            with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=['id', 'task_title', 'start_time', 'duration_minutes', 'fatigue_score', 'context_switches', 'is_completed'])
                writer.writeheader()
                for s in sessions:
                    writer.writerow(s)
            

            return JsonResponse({
                'status': 'success',
                'fatigue_score': calculated_fatigue,
                'cbt_prompt': cbt_prompt,
                'message': 'Session saved & CSV auto-exported successfully!'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'invalid method'}, status=405)

@login_required(login_url='/login/')
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return redirect('tasks')

@login_required(login_url='/login/')
def neural_quests_view(request):
    today = timezone.localdate()
    
    streak_obj, created = StreakTracker.objects.get_or_create(user=request.user)

    if streak_obj.last_completed_date:
        delta = (today - streak_obj.last_completed_date).days
        if delta > 1 and streak_obj.current_streak > 0:
            streak_obj.current_streak = 0
            streak_obj.total_broken_count += 1
            streak_obj.save()

    daily_quest = DailyUserQuest.objects.filter(user=request.user, assigned_date=today).first()
    
    if not daily_quest:
        all_quests = list(NeuralQuest.objects.all())
        if all_quests:
            selected_quest = random.choice(all_quests)
            daily_quest = DailyUserQuest.objects.create(
                user=request.user,
                quest=selected_quest,
                assigned_date=today
            )

    if request.method == 'POST' and daily_quest and not daily_quest.is_completed:
        action = request.POST.get('action')
        if action == 'complete':
            daily_quest.is_completed = True
            daily_quest.completed_at = timezone.now()
            daily_quest.save()

            if streak_obj.last_completed_date == today - datetime.timedelta(days=1):
                streak_obj.current_streak += 1
            elif streak_obj.last_completed_date != today:
                streak_obj.current_streak = 1
            
            if streak_obj.current_streak > streak_obj.longest_streak:
                streak_obj.longest_streak = streak_obj.current_streak
                
            streak_obj.last_completed_date = today
            streak_obj.save()
            return redirect('neural_quests')

    context = {
        'daily_quest': daily_quest,
        'streak': streak_obj,
    }
    return render(request, 'core/quests.html', context)