import math

from django.db import (
    transaction,
    IntegrityError
)
from django.db.models import (
    F,
    OuterRef
    )

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from cards.exceptions import (
    NotAuthenticated,
    InvalidData
)
from cards.models import (
    CardPossesionStatus,
    CardSellRegister
)
from cards.serializers import (
    CardSellRegisterListSerializer,
    CardSellRegisterCreateSerializer
)


class CardSellListView(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)

    def perform_authentication(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()

    def get(self, request):
        """
        1. sqlite3은 distinct on을 제공하지 않아 최소가격 및 수정일 기준 정렬 후 id를 가져옴
        2. 해당 ID가 일치하는 CardSellRegister를 가져와서 데이터 제공
        """

        minumum_price_card_ids = CardSellRegister.objects.filter(
            card_id=OuterRef("card_id"),
            state="selling",
        ).order_by("price", "-modified_at").values("id")[:1]

        card_sell_registers = (
            CardSellRegister.objects.filter(id__in=minumum_price_card_ids)
            .select_related("card", "user")
        )
        data = CardSellRegisterListSerializer(card_sell_registers, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)


class CardSellCreateView(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)

    def perform_authentication(self, request):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()

    def post(self, request, *args, **kwargs):
        user_id = self.request.user.id
        card_id = self.kwargs.get("card_id")
        quantity = self.request.data.get("quantity")
        price = self.request.data.get("price")
        fee = math.trunc(price * 0.2)

        try:
            with transaction.atomic():
                card_possesion_status = CardPossesionStatus.objects.get(
                    card_id=card_id,
                    user_id=user_id
                )
                card_possesion_status.quantity = F("quantity") - quantity
                card_possesion_status.save()
                card_sell_register = CardSellRegister.objects.create(
                    card_id=card_id,
                    price=price,
                    fee=fee,
                    quantity=quantity,
                    user_id=user_id
                )
        except IntegrityError:
            raise InvalidData(
                **{
                    "detail": "판매할 수량을 다시 확인해주세요",
                    "code": "InvalidQuantity"
                }
            )
        except CardPossesionStatus.DoesNotExist:
            raise InvalidData(
                **{
                    "detail": "판매할 카드가 없습니다",
                    "code": "InvalidCardId"
                }
            )
        data = CardSellRegisterCreateSerializer(card_sell_register).data
        return Response(data=data, status=status.HTTP_201_CREATED)
