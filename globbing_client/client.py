from typing import Optional
from selenium.webdriver import Chrome
from .http import RequestClient
from .auth import SessionManager, CaptchaSolver
from .exceptions import GlobbingException

class GlobbingClient:
    """Основной класс для работы с Globbing API"""
    
    def __init__(self, username: str, password: str, selenium_driver: Optional[Chrome] = None):
        """
        Инициализация клиента
        
        Args:
            username: Имя пользователя
            password: Пароль
            selenium_driver: Опциональный инстанс Selenium WebDriver
        """
        self._username = username
        self._password = password
        
        # Инициализация компонентов
        self._request_client = RequestClient()
        self._captcha_solver = CaptchaSolver(selenium_driver)
        self._session_manager = SessionManager(self._request_client, self._captcha_solver)

    def login(self) -> bool:
        """
        Выполняет вход в систему
        
        Returns:
            bool: True если вход успешен
            
        Raises:
            GlobbingException: При ошибке входа
        """
        return self._session_manager.login(self._username, self._password)

    def refresh_session(self) -> bool:
        """
        Обновляет сессию
        
        Returns:
            bool: True если обновление успешно
        """
        return self._session_manager.refresh(self._username, self._password)

    @property
    def http(self) -> RequestClient:
        """Возвращает HTTP клиент для выполнения запросов"""
        return self._request_client

    @property
    def session(self) -> SessionManager:
        """Возвращает менеджер сессии"""
        return self._session_manager

    def close(self):
        """Закрывает клиент и освобождает ресурсы"""
        self._session_manager.close()
