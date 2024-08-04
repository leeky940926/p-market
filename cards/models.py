from django.db import models

from utilities.models import TimeStampedModel

CARD_SELL_STATE = (
    ("selling", "판매중"),
    ("selled", "판매완료"),
    ("trading", "거래중"),
)


class Card(TimeStampedModel):
    """
    카드 모델: 시중에 판매되는 모든 카드에 대한 정보가 있는 테이블입니다.
    """
    name = models.CharField(max_length=100, verbose_name="카드 이름")


class CardSellRegister(TimeStampedModel):
    """
    카드 판매 등록 모델: 사용자가 카드를 판매하기 위해 등록하는 테이블입니다.
    """
    deleted_at = models.DateTimeField(null=True, verbose_name="등록삭제 날짜")
    selled_at = models.DateTimeField(null=True, verbose_name="판매완료 날짜")
    state = models.CharField(max_length=10, verbose_name="상태", choices=CARD_SELL_STATE, default="selling")
    card = models.ForeignKey("cards.Card", on_delete=models.PROTECT, verbose_name="카드")
    price = models.PositiveIntegerField(verbose_name="가격")
    fee = models.PositiveIntegerField(verbose_name="수수료")
    user = models.ForeignKey("users.User", on_delete=models.PROTECT, verbose_name="판매자")

    class Meta:
        verbose_name_plural = "카드 판매 등록"


class CardSellHistory(TimeStampedModel):
    """
    카드 판매 이력 모델: 카드 판매 등록이 완료되면 이력을 저장하는 테이블입니다.
    """
    card_sell_register = models.ForeignKey("cards.CardSellRegister", on_delete=models.PROTECT, verbose_name="카드 판매 등록")

    class Meta:
        verbose_name_plural = "카드 판매 이력"


class CardBuyHistory(TimeStampedModel):
    """
    카드 구매 이력 모델: 카드 구매가 완료되면 이력을 저장하는 테이블입니다.
    """
    card_sell_register = models.ForeignKey("cards.CardSellRegister", on_delete=models.PROTECT, verbose_name="카드 판매 등록")
    user = models.ForeignKey("users.User", on_delete=models.PROTECT, verbose_name="구매자")

    class Meta:
        verbose_name_plural = "카드 구매 이력"
