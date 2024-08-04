from rest_framework import serializers

from cards.models import CardSellRegister


class CardSellRegisterListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    cardId = serializers.IntegerField(source="card.id")
    price = serializers.IntegerField()
    userId = serializers.IntegerField(source="user.id")
    nickname = serializers.CharField(source="user.nickname")

    class Meta:
        model = CardSellRegister
        fields = ("id", "cardId", "price", "userId", "nickname")
