from django.db import models
from django.contrib.auth.models import User
import datetime

class DailyCheckIn(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    starting_mood = models.CharField(max_length=50)
    energy_level = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
class WorkSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_title = models.CharField(max_length=255, default="General Focus Session")
    start_time = models.DateTimeField(auto_now_add=True)
    duration_minutes = models.IntegerField(default=25)
    fatigue_score = models.FloatField(default=0.0)
    context_switches = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.task_title}"

class CBTIntervention(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trigger_reason = models.CharField(max_length=100)
    prompt_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    category = models.CharField(max_length=50, default='General') # e.g., Coding, Study, Personal
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.priority})"

class MotivationalVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class NeuralQuest(models.Model):
    category_choices = [
        ('Physical', 'Physical Health'),
        ('Mind', 'Psychology & Mindset'),
        ('DeepWork', 'Deep Work & Productivity'),
        ('Growth', 'Self-Growth & Learning'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=category_choices, default='Mind')

    def __str__(self):
        return self.title

class DailyUserQuest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quest = models.ForeignKey(NeuralQuest, on_delete=models.CASCADE)
    assigned_date = models.DateField(default=datetime.date.today)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.quest.title} ({self.assigned_date})"

class StreakTracker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_completed_date = models.DateField(null=True, blank=True)
    total_broken_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Streak: {self.current_streak} days (Longest: {self.longest_streak})"