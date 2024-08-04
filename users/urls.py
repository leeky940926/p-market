from django.urls import path

from users.views import LoginView

urlpatterns = [
    path("users", LoginView.as_view()),
]
