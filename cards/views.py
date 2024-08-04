from django.db.models import OuterRef

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from cards.exceptions import NotAuthenticated
from cards.models import CardSellRegister
from cards.serializers import CardSellRegisterListSerializer


class SellListView(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)

    def perform_authentication(self, request):
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
