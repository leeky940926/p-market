from rest_framework import exceptions


class NotAuthenticated(exceptions.APIException):
    status_code = 401
    default_detail = "로그인이 필요합니다."
    default_code = "LoginRequired"


class InvalidData(exceptions.APIException):
    status_code = 422
    default_detail = "잘못 입력된 데이터입니다."
    default_code = "InvalidData"
