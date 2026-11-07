from django import forms
from .models import Task, MotivationalVideo

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg', 
                'placeholder': 'Enter task title...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Task details or notes (optional)...'
            }),
        }

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = MotivationalVideo
        fields = ['title', 'video_file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Video title...'}),
            'video_file': forms.FileInput(attrs={'class': 'form-control'}),
        }