from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

urlpatterns = [
    path("ping-config/", lambda r: HttpResponse("CONFIG OK")),  # тест
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("core.urls")),
]