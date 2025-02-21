from django import forms
from .models import Task
from datetime import datetime

class TaskForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'id': 'deadline'})
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
