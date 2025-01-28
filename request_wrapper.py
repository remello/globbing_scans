import requests
import time
import logging
from typing import Optional, Dict, Any
from requests.exceptions import RequestException

class RequestWrapper:
    def __init__(self, session: Optional[requests.Session] = None, max_retries: int = 3, retry_delay: int = 1):
        self._session = session or requests.Session()
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._logger = logging.getLogger(__name__)

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Выполняет HTTP запрос с повторными попытками при ошибках"""
        for attempt in range(self._max_retries):
            try:
                response = getattr(self._session, method.lower())(url, **kwargs)
                response.raise_for_status()
                return response
            except RequestException as e:
                self._logger.error(f"Attempt {attempt + 1}/{self._max_retries} failed: {str(e)}")
                if attempt == self._max_retries - 1:
                    raise
                time.sleep(self._retry_delay)

    def get(self, url: str, **kwargs) -> requests.Response:
        """Выполняет GET запрос"""
        return self._make_request('GET', url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        """Выполняет POST запрос"""
        return self._make_request('POST', url, **kwargs)

    def get_session(self) -> requests.Session:
        """Возвращает текущую сессию"""
        return self._session

    def set_session(self, session: requests.Session):
        """Устанавливает новую сессию"""
        self._session = session
