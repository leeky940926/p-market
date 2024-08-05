from rest_framework import serializers

from cards.models import (
    CardSellHistory,
    CardSellRegister,
    CardBuyHistory
)


class CardSellRegisterListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    createdAt = serializers.DateTimeField(source="created_at")
    cardId = serializers.IntegerField(source="card.id")
    price = serializers.IntegerField()
    quantity = serializers.IntegerField()
    userId = serializers.IntegerField(source="user.id")
    nickname = serializers.CharField(source="user.nickname")

    class Meta:
        model = CardSellRegister
        fields = ("id", "createdAt", "cardId", "price", "quantity", "userId", "nickname")


class CardSellRegisterCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    createdAt = serializers.DateTimeField(source="created_at")
    cardId = serializers.IntegerField(source="card.id")
    price = serializers.IntegerField()
    state = serializers.CharField()
    quantity = serializers.IntegerField()
    userId = serializers.IntegerField(source="user.id")

    class Meta:
        model = CardSellRegister
        fields = ("id", "createdAt", "cardId", "price", "state", "quantity", "userId")


class CardBuyHistorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    cardId = serializers.IntegerField(source="card.id")
    quantity = serializers.IntegerField(source="CardSellRegister.quantity")
    userId = serializers.IntegerField(source="user.id")
    nickname = serializers.CharField(source="user.nickname")

    class Meta:
        model = CardBuyHistory
        fields = ("id", "cardId", "quantity", "userId", "nickname")


class CardSellHistoryListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    createdAt = serializers.DateTimeField(source="created_at")
    price = serializers.IntegerField(source="card_sell_register.price")
    fee = serializers.IntegerField(source="card_sell_register.fee")
    quantity = serializers.IntegerField(source="card_sell_register.quantity")
    selledAt = serializers.DateTimeField(source="card_sell_register.selled_at")
    cardId = serializers.IntegerField(source="card_sell_register.card.id")
    cardName = serializers.CharField(source="card_sell_register.card.name")

    class Meta:
        model = CardSellHistory
        fields = ("id", "createdAt", "price", "fee", "quantity", "selledAt", "cardId", "cardName")
