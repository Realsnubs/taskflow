from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"api/projects", views.ProjectViewSet)
router.register(r"api/tasks", views.TaskViewSet)
router.register(r"api/comments", views.CommentViewSet)
router.register(r"api/memberships", views.MembershipViewSet)

urlpatterns = [
    path("projects/", views.project_list),
    path("projects/new/", views.project_create),
    path("projects/<int:project_id>/board/", views.project_board),
    path("projects/<int:project_id>/tasks/new/", views.task_create),
    path("projects/<int:project_id>/tasks/<int:task_id>/set/<str:status>/", views.task_set_status),
    path("projects/<int:project_id>/tasks/<int:task_id>/delete/", views.task_delete),
    path("projects/<int:project_id>/tasks/<int:task_id>/comment/", views.add_comment),
    path("projects/<int:project_id>/members/", views.project_members),
    path("projects/<int:project_id>/delete/", views.project_delete),
]

urlpatterns += router.urls