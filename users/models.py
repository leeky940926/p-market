from django.db import (
    models,
    transaction,
    IntegrityError
)

from cards.models import Card, CardPossesionStatus
from utilities.models import TimeStampedModel
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)


class UserManager(BaseUserManager):
    def create_user(self, email, nickname, password=None):
        """
        주어진 이메일, 닉네임, 비밀번호 등 개인정보로 User 인스턴스 생성
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            nickname=nickname,
        )

        user.set_password(password)
        try:
            with transaction.atomic():
                user.save(using=self._db)

                """
                사용자가 생성되면 사용자의 잔액과 카드 소유 현황을 생성한다.
                """
                UserBalance.objects.create(user=user)
                cards = Card.objects.all()
                bulk_create_list = [
                    CardPossesionStatus(
                        user_id=user.id, card_id=card.id, quantity=0
                    ) for card in cards
                ]
                CardPossesionStatus.objects.bulk_create(bulk_create_list)
        except IntegrityError:
            raise ValueError('User already exists')
        return user


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    사용자 모델
    """
    email = models.EmailField(unique=True, verbose_name='이메일')
    nickname = models.CharField(max_length=30, verbose_name='닉네임')
    is_superuser = models.BooleanField(default=False, verbose_name='최상위 사용자 여부')

    objects = UserManager()

    USERNAME_FIELD = 'email'


class UserBalance(TimeStampedModel):
    """
    사용자 잔액 모델: 사용자가 보유한 잔액을 저장하는 테이블입니다.
    """
    user = models.OneToOneField("users.User", on_delete=models.PROTECT, verbose_name='사용자')
    balance = models.PositiveIntegerField(default=0, verbose_name='잔액')

    class Meta:
        verbose_name_plural = '사용자 보유 잔액'
