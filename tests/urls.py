from django.contrib.auth import views
from django.urls import include, path

urlpatterns = [
    # accounts
    path("accounts/login/", views.LoginView.as_view()),
    path("accounts/logout/", views.LogoutView.as_view()),
    # folders
    path("", include("coconuts.urls")),
]
