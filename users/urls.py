from django.urls import path

from users.views import LoginView

urlpatterns = [
    path("users/login", LoginView.as_view()),
]
