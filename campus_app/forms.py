from django import forms
from .models import Assignment, Notification

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['course', 'title', 'description', 'due_date']

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['message']