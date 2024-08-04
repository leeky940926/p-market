from rest_framework import exceptions


class NotAuthenticated(exceptions.APIException):
    status_code = 401
    default_detail = "로그인이 필요합니다."
    default_code = "LoginRequired"
