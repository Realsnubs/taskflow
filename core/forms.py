from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]

from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "status", "priority", "deadline"]

        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"})
        }


from .models import Membership

class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ["user", "role"]


from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]