from django.urls import path

from cards.views import (
    CardSellListView,
    CardSellCreateView,
    CardBuyCreateView,
    CardSellHistoryListView
)

urlpatterns = [
    path("cards/sells", CardSellListView.as_view()),
    path("cards/<int:card_id>/sells", CardSellCreateView.as_view()),
    path("cards/<int:card_id>/buys", CardBuyCreateView.as_view()),
    path("cards/<int:card_id>/sells/histories", CardSellHistoryListView.as_view()),
]
