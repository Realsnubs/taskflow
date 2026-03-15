from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Project(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class Membership(models.Model):
    ROLE_OWNER = "owner"
    ROLE_MANAGER = "manager"
    ROLE_MEMBER = "member"
    ROLE_CHOICES = [
        (ROLE_OWNER, "Owner"),
        (ROLE_MANAGER, "Manager"),
        (ROLE_MEMBER, "Member"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)

    class Meta:
        unique_together = ("user", "project")

    def __str__(self):
        return f"{self.user} -> {self.project} ({self.role})"
    



class Task(models.Model):
    STATUS_CHOICES = [
        ("todo", "To do"),
        ("in_progress", "In progress"),
        ("done", "Done"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="todo")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    



from django.contrib.auth.models import User
from django.utils import timezone

class Comment(models.Model):
    task = models.ForeignKey("Task", on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.author} - {self.task}"
    