from django.shortcuts import render, redirect
from .models import Project
from .forms import ProjectForm, TaskForm
from django.contrib.auth.decorators import login_required

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

    todo = Task.objects.filter(project=project, status="todo")
    in_progress = Task.objects.filter(project=project, status="in_progress")
    done = Task.objects.filter(project=project, status="done")

    return render(request, "project_board.html", {
        "project": project,
        "todo": todo,
        "in_progress": in_progress,
        "done": done,
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
    project = get_object_or_404(Project, id=project_id, memberships__user=request.user)

    my_membership = Membership.objects.get(project=project, user=request.user)
    if my_membership.role not in (Membership.ROLE_OWNER, Membership.ROLE_MANAGER):
        return redirect(f"/projects/{project.id}/board/")

    members = Membership.objects.filter(project=project).select_related("user").order_by("role", "user__username")

    if request.method == "POST":
        form = MembershipForm(request.POST)
        if form.is_valid():
            m = form.save(commit=False)
            m.project = project
            m.save()
            return redirect(f"/projects/{project.id}/members/")
    else:
        form = MembershipForm()

    return render(request, "project_members.html", {"project": project, "members": members, "form": form})




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