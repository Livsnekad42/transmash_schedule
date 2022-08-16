import ssl
import asyncio
from typing import Union, Dict

from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from asgiref.sync import async_to_sync
from django.conf import settings

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

import httpx

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


class BaseProxyApi:
    permission_classes = (AllowAny,)
    serializer_class = None
    
    def valid_request(self, request) -> Union[str, None]:
        if request.data.get("token"):
            return request.data["token"]
        
        return None


class BaseRequestsAPI:
    timeout = (20, 30)
    
    async def arequest_post(self, url, headers={}, json=None, data=None):
        async with httpx.AsyncClient(timeout=self.timeout, headers=headers) as client:
            return await client.post(url, json=json, data=data)

    def request_post(self, url,  headers={}, json=None, data=None):
        with httpx.Client(timeout=self.timeout, headers=headers) as client:
            return client.post(url, json=json, data=data)
        
    async def arequest_get(self, url, headers={}, params={}):
        async with httpx.AsyncClient(timeout=self.timeout, headers=headers, params=params) as client:
            return await client.get(url)

    def request_get(self, url, headers={}, params={}):
        with httpx.Client(timeout=self.timeout, headers=headers, params=params) as client:
            return client.get(url)
        
    def get_errors(self, response) -> Union[dict, None]:
        if response.get("errors") and len(response["errors"]) > 0:
            _error = []
            for _err in response["errors"]:
                if _err.get("code"):
                    if _err["code"] == settings.PERMISSION_DENIED_API_CODE:
                        raise PermissionDenied()
                    if _err["code"] in settings.PUBLIC_ERROR_CODE:
                        _error.append(_err)
            if len(_error) > 0:
                return {"errors": _error}
            
        return None


REQUEST = BaseRequestsAPI()


class BaseViewFromAPI(APIView, BaseRequestsAPI):
    permission_classes = (AllowAny,)
    serializer_class = None
    endpoint_api = None
    
    @method_decorator(async_to_sync)
    async def post(self, request):
        if not self.serializer_class:
            raise Exception("Serializer class not initialized")
        
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            task = self.arequest_post(self.endpoint_api, data)
            try:
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None

                if loop and loop.is_running():
                    resp = await task

                else:
                    resp = asyncio.run(task)

            except (httpx.ConnectTimeout, httpx.ReadTimeout):
                return Response({"errors": [{"code": "api", "text": "Непредвиденная ошибка"}]},
                                status=status.HTTP_400_BAD_REQUEST)
            
            return self._response(resp)

        return Response({"error_fields": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def sync_post(self, request):
        if not self.serializer_class:
            raise Exception("Serializer class not initialized")

        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            try:
                resp = self.request_post(self.endpoint_api, data)

            except (httpx.ConnectTimeout, httpx.ReadTimeout):
                return Response({"errors": [{"code": "api", "text": "Непредвиденная ошибка"}]},
                                status=status.HTTP_400_BAD_REQUEST)

            return self._response(resp)

        return Response({"error_fields": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_token(request) -> Union[str, None]:
        if request.data.get("token"):
            return request.data["token"]
    
        return None

    def _response(self, resp: httpx.Response) -> Response:
        try:
            resp_data = resp.json()

            try:
                errors = self.get_errors(resp_data)

            except PermissionDenied:
                return Response({"errors": [{"code": 4, "text": "Срок действия сессии истек"}]},
                                status=status.HTTP_403_FORBIDDEN)

            if errors:
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(resp_data["data"], status=status.HTTP_200_OK)

        except Exception as err:
            return Response({"errors": [{"code": "api", "text": str(err)}]},
                            status=status.HTTP_400_BAD_REQUEST)

