import requests
import settings

from emnify.errors import UnauthorisedException, JsonDecodeException, UnknownStatusCodeException
from emnify.modules.api.models import AuthenticationResponse
from emnify.constants import RequestsTypeEnum, RequestsUrlEnum, RequestDefaultHeadersKeys, RequestDefaultHeadersValues


class BaseApiManager:
    """
    Base manager for api calls handling
    """

    response_handlers = {
        200: 'return_unwrapped',
        201: 'return_success',
        401: 'unauthorised',
    }

    request_url_prefix = ''
    request_method_name = ''

    @staticmethod
    def _build_headers(token=''):
        return {
            RequestDefaultHeadersKeys.ACCEPT.value: RequestDefaultHeadersValues.APPLICATION_JSON.value,
            RequestDefaultHeadersKeys.AUTHORIZATION.value: RequestDefaultHeadersValues.BEARER_TOKEN.value.format(token)
        }

    def build_method_url(self, url_params):
        return self.request_url_prefix.format(**url_params)

    def unauthorised(self, response: requests.Response, client, data: dict = None, path_params=None, *args, **kwargs):
        """
        method for 1 cycle retry - re authentication
        """
        auth = Authenticate()
        client.token = AuthenticationResponse(
            **auth.call_api(client, {"application_token": client.app_token})
        ).auth_token

        return self.call_api(client, data, path_params=path_params, *args, **kwargs)

    def call_api(self, client, data: dict = None, files=None, path_params: dict = None, query_params: dict = None):
        url = self.request_url_prefix
        if path_params:
            url = self.build_method_url(path_params)
        response = self.make_request(client, url, data, files, query_params=query_params)
        if response.status_code not in self.response_handlers.keys():
            raise UnknownStatusCodeException(
                "Unknown status code {status_code}".format(status_code=response.status_code)
            )
        return getattr(self, self.response_handlers[response.status_code])\
            (response, client, data=data, files=files, query_params=query_params, path_params=path_params)

    def make_get_request(self, main_url: str, method_name: str, headers: dict, params: str = None):
        return requests.get(self.resource_path(main_url, method_name), headers=headers, params=params)

    def make_post_request(self, main_url: str, method_name: str, headers: dict, params: dict = None, data: dict = None):
        return requests.post(self.resource_path(main_url, method_name), headers=headers, json=data, params=params)

    def make_patch_request(self, main_url: str, method_name: str, headers: dict, params: dict = None, data: dict = None):
        return requests.patch(self.resource_path(main_url, method_name), headers=headers, json=data, params=params)

    def make_request(self, client, method_url: str, data=None, files=None, query_params=None):
        if self.request_method_name not in RequestsTypeEnum.list():
            raise ValueError(f'{self.request_method_name}: This method is not allowed')
        headers = self._build_headers(client.token)
        response = None
        if self.request_method_name == RequestsTypeEnum.GET.value:
            response = self.make_get_request(
                settings.MAIN_URL, method_url, headers=headers, params=query_params
            )
        elif self.request_method_name == RequestsTypeEnum.POST.value:
            response = self.make_post_request(
                settings.MAIN_URL, method_url, headers=headers, params=query_params, data=data
            )
        elif self.request_method_name == RequestsTypeEnum.PATCH.value:
            response = self.make_patch_request(
                settings.MAIN_URL, method_url, headers=headers, params=query_params, data=data
            )
        return response

    @staticmethod
    def return_success(*_, **__) -> True:
        return True

    @staticmethod
    def return_unwrapped(response: requests.Response, *args, **kwargs) -> requests.Response.json:
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            raise JsonDecodeException('error while parsing json for')

    @staticmethod
    def resource_path(main_url: str, method_name: str):
        return f'{main_url}{method_name}'


class Authenticate(BaseApiManager):
    request_url_prefix = RequestsUrlEnum.V1_AUTHENTICATE.value
    request_method_name = RequestsTypeEnum.POST.value

    response_handlers = {
        200: 'return_unwrapped',
        401: 'unauthorised',
        404: 'unexpected_error'
    }

    def unauthorised(
            self, response: requests.Response, client, data: dict = None, files=None, path_params: list = None, **kwargs
    ):
        raise UnauthorisedException('Invalid Application Token')

    def unexpected_error(
            self, response: requests.Response, client, data: dict = None, files=None, path_params: list = None
    ):
        raise UnauthorisedException(f'Unexpected Auth Error {response.json()}')
