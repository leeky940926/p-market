import math
from datetime import datetime

from django.db import (
    transaction,
    IntegrityError
)
from django.db.models import (
    F,
    OuterRef,
    Q
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
    CardBuyHistory,
    CardPossesionStatus,
    CardSellHistory,
    CardSellRegister
)
from cards.serializers import (
    CardSellHistoryListSerializer,
    CardSellRegisterListSerializer,
    CardSellRegisterCreateSerializer
)
from users.models import UserBalance


class CardSellListView(APIView):
    def get(self, request):
        """
        1. sqlite3은 distinct on을 제공하지 않아 최소가격 및 수정일 기준 정렬 후 id를 가져옴
        2. 해당 ID가 일치하는 CardSellRegister를 가져와서 데이터 제공
        """

        minumum_price_card_ids = CardSellRegister.objects.filter(
            card_id=OuterRef("card_id"),
            state="selling",
            deleted_at__isnull=True
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
                # 현재 보유정보를 가져온 후 판매할 수량을 차감
                card_possesion_status = CardPossesionStatus.objects.get(
                    card_id=card_id,
                    user_id=user_id
                )
                card_possesion_status.quantity = F("quantity") - quantity
                card_possesion_status.save()

                # 판매 등록
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


class CardBuyCreateView(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)

    def perform_authentication(self, request):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()

    def post(self, request, *args, **kwargs):
        user_id = self.request.user.id
        card_id = self.kwargs.get("card_id")

        try:
            with transaction.atomic():
                # 최소 가격으로 등록된 판매 정보(단, 본인이 등록한 건 나오지 않음)
                card_sell_register = CardSellRegister.objects.filter(
                    Q(deleted_at__isnull=True) &
                    Q(card_id=card_id) &
                    Q(state="selling") &
                    ~Q(user_id=user_id)
                ).latest("-price")

                # 타인이 거래 시도를 못 하게 상태 변경
                card_sell_register.state = "trading"
                card_sell_register.save()

                # 구매자 액션: 현재 보유정보를 가져온 후 구매할 수량을 추가
                card_possesion_status = CardPossesionStatus.objects.get(
                    card_id=card_id,
                    user_id=user_id
                )
                card_possesion_status.quantity = F("quantity") + card_sell_register.quantity
                card_possesion_status.save()

                # 구매자 액션: 금액 차감(가격+수수료 차감)
                buyer_balance = UserBalance.objects.get(user_id=user_id)
                buyer_balance.balance = F("balance") - card_sell_register.price - card_sell_register.fee
                buyer_balance.save()

                # 구매자 액션: 구매내역 등록
                CardBuyHistory.objects.create(
                    card_sell_register_id=card_sell_register.id,
                    user_id=user_id
                )

                # 판매자 액션: 판매내역 등록
                CardSellHistory.objects.create(
                    card_sell_register_id=card_sell_register.id
                )

                # 판매자 액션: 판매 정보 업데이트
                card_sell_register.state = "selled"
                card_sell_register.selled_at = datetime.now()
                card_sell_register.save()

                # 판매자 액션: 금액 입금(가격+수수료 입금)
                seller_balance = UserBalance.objects.get(user_id=card_sell_register.user_id)
                seller_balance.balance = F("balance") + card_sell_register.price + card_sell_register.fee
                seller_balance.save()
        except IntegrityError:
            raise InvalidData(
                **{
                    "detail": "구매 입력 데이터를 다시 확인해주세요",
                }
            )
        data = CardSellRegisterCreateSerializer(card_sell_register).data
        return Response(data=data, status=status.HTTP_201_CREATED)


class CardSellHistoryListView(APIView):
    def get(self, request, *args, **kwargs):
        card_id = self.kwargs.get("card_id")

        # card_id의 최근 거래가를 5개 조회
        card_sell_histories = CardSellHistory.objects.filter(
            card_sell_register__card_id=card_id
        ).select_related("card_sell_register__card").order_by("-created_at")[:5]

        data = CardSellHistoryListSerializer(card_sell_histories, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)
