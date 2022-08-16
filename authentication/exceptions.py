from rest_framework.exceptions import APIException, ErrorDetail
from rest_framework import status


class UserBannedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Access error"
    default_code = 'banned'
    
    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        
        self.detail = ErrorDetail(detail, code)
