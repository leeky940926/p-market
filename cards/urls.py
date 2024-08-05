from django.urls import path

from cards.views import (
    CardSellListView,
    CardSellCreateView,
    CardBuyCreateView
)

urlpatterns = [
    path("cards/sells", CardSellListView.as_view()),
    path("cards/<int:card_id>/sells", CardSellCreateView.as_view()),
    path("cards/<int:card_id>/buys", CardBuyCreateView.as_view()),
]
