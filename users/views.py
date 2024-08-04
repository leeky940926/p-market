from rest_auth.utils import jwt_encode
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.exceptions import NotExistData, InvalidData
from users.models import User


class LoginView(APIView):
    def post(self, request):
        email = self.request.data.get("email")
        password = self.request.data.get("password")

        #  유저 정보 불러오기
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise NotExistData(
                **{
                    "detail": "존재하지 않는 사용자입니다.",
                    "code": "NotExistUser",
                }
            )

        # 비밀번호 확인
        check_password = user.check_password(password)
        if not check_password:
            raise InvalidData(
                **{
                    "detail": "비밀번호가 일치하지 않습니다.",
                    "code": "InvalidPassword",
                }
            )

        # 신원인증 성공에 따른 토큰 발급
        token = jwt_encode(user)
        return Response({"token": token}, status=status.HTTP_200_OK)
