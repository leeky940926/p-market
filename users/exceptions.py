from rest_framework import exceptions


class NotExistData(exceptions.APIException):
    status_code = 404
    default_detail = "존재하지 않는 데이터입니다."
    default_code = "NotExistData"


class InvalidData(exceptions.APIException):
    status_code = 422
    default_detail = "잘못된 데이터입니다."
    default_code = "InvalidData"
