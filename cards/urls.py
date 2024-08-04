from django.urls import path

from cards.views import SellListView

urlpatterns = [
    path("cards/sells", SellListView.as_view())
]
