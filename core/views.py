from django.shortcuts import render, redirect, get_object_or_404
from .models import Project
from .forms import ProjectForm, TaskForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def custom_logout(request):
    logout(request)
    return redirect("/accounts/login/")

@login_required
def project_list(request):
    projects = Project.objects.filter(memberships__user=request.user).distinct()
    return render(request, "project_list.html", {"projects": projects})

@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            from .models import Membership  # если нет импорта сверху
            Membership.objects.create(user=request.user, project=project, role=Membership.ROLE_OWNER)
            
            return redirect("/projects/")
    else:
        form = ProjectForm()

    return render(request, "project_form.html", {"form": form})


from django.shortcuts import get_object_or_404
from .models import Task

@login_required
def project_board(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    status_filter = request.GET.get("status", "")
    priority_filter = request.GET.get("priority", "")

    tasks = Task.objects.filter(project=project)

    if status_filter:
        tasks = tasks.filter(status=status_filter)

    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    todo = tasks.filter(status="todo")
    in_progress = tasks.filter(status="in_progress")
    done = tasks.filter(status="done")

    return render(request, "project_board.html", {
    "project": project,
    "todo": todo,
    "in_progress": in_progress,
    "done": done,
    "status_filter": status_filter,
    "priority_filter": priority_filter,
    "today": timezone.now().date(),
})

@login_required
def task_create(request, project_id):
    project = get_object_or_404(Project, id=project_id, memberships__user=request.user)

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            return redirect(f"/projects/{project.id}/board/")
    else:
        form = TaskForm()

    return render(request, "task_form.html", {"form": form, "project": project})



from django.views.decorators.http import require_POST


@login_required
@require_POST
def task_set_status(request, project_id, task_id, status):
    project = get_object_or_404(Project, id=project_id, memberships__user=request.user)
    task = get_object_or_404(Task, id=task_id, project=project)

    allowed = {"todo", "in_progress", "done"}
    if status not in allowed:
        return redirect(f"/projects/{project.id}/board/")

    task.status = status
    task.save()
    return redirect(f"/projects/{project.id}/board/")




from django.views.decorators.http import require_POST


@login_required
@require_POST
def task_delete(request, project_id, task_id):
    project = get_object_or_404(Project, id=project_id, memberships__user=request.user)
    task = get_object_or_404(Task, id=task_id, project=project)

    task.delete()
    return redirect(f"/projects/{project.id}/board/")



from .forms import MembershipForm
from .models import Membership

@login_required
def project_members(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    memberships = Membership.objects.filter(project=project).select_related("user")

    existing_user_ids = memberships.values_list("user_id", flat=True)

    if request.method == "POST":
        form = MembershipForm(request.POST)
        form.fields["user"].queryset = form.fields["user"].queryset.exclude(id__in=existing_user_ids)

        if form.is_valid():
            membership = form.save(commit=False)
            membership.project = project
            membership.save()
            return redirect(f"/projects/{project.id}/members/")
    else:
        form = MembershipForm()
        form.fields["user"].queryset = form.fields["user"].queryset.exclude(id__in=existing_user_ids)

    return render(request, "project_members.html", {
        "project": project,
        "memberships": memberships,
        "form": form,
    })




from .models import Comment
from .forms import CommentForm
from django.views.decorators.http import require_POST

@require_POST
@login_required
def add_comment(request, project_id, task_id):
    project = get_object_or_404(Project, id=project_id, memberships__user=request.user)
    task = get_object_or_404(Task, id=task_id, project=project)

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.task = task
        comment.author = request.user
        comment.save()

    return redirect(f"/projects/{project.id}/board/")



from django.views.decorators.http import require_POST

@require_POST
@login_required
def project_delete(request, project_id):
    project = get_object_or_404(Project, id=project_id, memberships__user=request.user)

   
    membership = Membership.objects.get(project=project, user=request.user)
    if membership.role != Membership.ROLE_OWNER:
        return redirect("/projects/")

    project.delete()
    return redirect("/projects/")


from rest_framework import viewsets
from .serializers import (
    ProjectSerializer,
    TaskSerializer,
    CommentSerializer,
    MembershipSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer


def landing_page(request):
    return render(request, "landing.html")
    



def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/projects/")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})



def remove_member(request, project_id, membership_id):
    membership = get_object_or_404(Membership, id=membership_id, project_id=project_id)

    if membership.role != "owner":
        membership.delete()

    return redirect(f"/projects/{project_id}/members/")


def task_edit(request, project_id, task_id):
    project = get_object_or_404(Project, id=project_id)
    task = get_object_or_404(Task, id=task_id, project=project)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect(f"/projects/{project.id}/board/")
    else:
        form = TaskForm(instance=task)

    return render(request, "task_form.html", {
        "form": form,
        "project": project,
        "task": task,
        "is_edit": True,
    })