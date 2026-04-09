from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import HttpResponse
from core.views import landing_page
from core.views import landing_page, register_view


def custom_logout(request):
    logout(request)
    return redirect("/accounts/login/")


urlpatterns = [
    path("ping-config/", lambda r: HttpResponse("CONFIG OK")),
    path("admin/", admin.site.urls),

    path("logout/", custom_logout, name="custom_logout"),
    path("accounts/", include("django.contrib.auth.urls")),

    path("", landing_page, name="landing"),
    path("", include("core.urls")),

    path("register/", register_view, name="register"),
]