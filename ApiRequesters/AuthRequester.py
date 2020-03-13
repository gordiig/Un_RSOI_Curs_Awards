import requests
from typing import Tuple
from django.conf import settings
from ApiRequesters.BaseApiRequester import BaseApiRequester
from ApiRequesters.exceptions import JsonDecodeError, UnexpectedResponse, RequestError


class AuthRequester(BaseApiRequester):
    """
    Реквестер к сервису авторизации
    """
    def __init__(self):
        super().__init__()
        self.host = settings.ENV['AUTH_HOST']

    def get_user_info(self, token: str) -> Tuple[requests.Response, dict]:
        """
        Получение инфы о юзере по токену (/api/user_info/)
        @param token: Токен
        @return: Джсон-описание юзера
        """
        auth_tuple = self._create_auth_header_tuple(token)
        auth_header = {auth_tuple[0]: auth_tuple[1]}
        response = self.get('user_info/', headers=auth_header)
        self._validate_return_code(response, 200)
        user_json = self._get_json_from_response(response)
        return response, user_json

    def is_moderator(self, token: str) -> bool:
        """
        Проверка по токену, является ли юзер модератором
        @param token: Токен
        @return: True, если модератор
        """
        response, user_json = self.get_user_info(token)
        try:
            return user_json['is_moderator']
        except KeyError:
            raise UnexpectedResponse(response=response, message='В джсоне юзера отсутствует поле is_moderator')

    def is_superuser(self, token: str) -> bool:
        """
        Проверка по токену, является ли юзер суперюзером
        @param token: Токен
        @return: True, если модератор
        """
        response, user_json = self.get_user_info(token)
        try:
            return user_json['is_superuser']
        except KeyError:
            raise UnexpectedResponse(response=response, message='В джсоне юзера отсутствует поле is_superuser')

