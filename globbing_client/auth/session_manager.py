import threading
import time
from typing import Optional
from bs4 import BeautifulSoup
from ..exceptions import AuthenticationError, SessionError
from ..http import RequestClient
from .captcha_solver import CaptchaSolver

class SessionManager:
    """Управление сессией и аутентификацией"""
    
    def __init__(self, request_client: RequestClient, captcha_solver: CaptchaSolver):
        """
        Инициализация менеджера сессии
        
        Args:
            request_client: HTTP клиент для выполнения запросов
            captcha_solver: Решатель капчи
        """
        self._request_client = request_client
        self._captcha_solver = captcha_solver
        self._is_logged_in = False
        self._keep_alive_thread = None
        self._stop_keep_alive = threading.Event()

    def login(self, username: str, password: str) -> bool:
        """
        Выполняет авторизацию пользователя
        
        Args:
            username: Имя пользователя
            password: Пароль
            
        Returns:
            bool: True если авторизация успешна
            
        Raises:
            AuthenticationError: При ошибке авторизации
        """
        try:
            login_url = "https://kz.globbing.com/ru/login/"
            
            # Получаем reCAPTCHA токен
            recaptcha_value = self._captcha_solver.get_token(login_url)

            # Получаем _token со страницы логина
            response = self._request_client.get(login_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            token_input = soup.find('input', {'name': '_token'})
            if not token_input:
                raise AuthenticationError("Failed to get _token")
            token = token_input.get('value')

            # Подготавливаем данные для авторизации
            data = {
                'email': username,
                'password': password,
                'g-recaptcha-response': recaptcha_value,
                '_token': token
            }

            # Заголовки запроса
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': login_url
            }

            # Выполняем авторизацию
            login_response = self._request_client.post(login_url, data=data, headers=headers)

            # Проверяем ответ
            try:
                json_data = login_response.json()
                if 'data' in json_data and json_data['data'].get('message') == 'globbing.login.success':
                    redirect_url = json_data['data'].get('redirect_url', 'https://kz.globbing.com/ru')
                    self._request_client.get(redirect_url)
                    self._is_logged_in = True
                    self.start_keep_alive()
                    return True
                else:
                    raise AuthenticationError(f"Login failed: {json_data}")
            except ValueError:
                # Если ответ не JSON, проверяем редирект
                if login_response.url != login_url:
                    self._is_logged_in = True
                    self.start_keep_alive()
                    return True
                else:
                    raise AuthenticationError("Login failed: Invalid response format")

        except Exception as e:
            raise AuthenticationError(f"Login failed: {str(e)}")

    def _keep_alive(self):
        """Фоновый поток для поддержания сессии активной"""
        while not self._stop_keep_alive.is_set():
            try:
                if self._is_logged_in:
                    self._request_client.get("https://kz.globbing.com/ru/profile/my-orders")
            except Exception as e:
                print(f"Keep-alive error: {e}")
            time.sleep(120)  # Ждем 2 минуты

    def start_keep_alive(self):
        """Запускает фоновый поток для поддержания сессии"""
        if not self._keep_alive_thread or not self._keep_alive_thread.is_alive():
            self._stop_keep_alive.clear()
            self._keep_alive_thread = threading.Thread(target=self._keep_alive, daemon=True)
            self._keep_alive_thread.start()

    def stop_keep_alive(self):
        """Останавливает фоновый поток"""
        if self._keep_alive_thread and self._keep_alive_thread.is_alive():
            self._stop_keep_alive.set()
            self._keep_alive_thread.join(timeout=1)

    def refresh(self, username: str, password: str) -> bool:
        """
        Выполняет повторную авторизацию
        
        Args:
            username: Имя пользователя
            password: Пароль
            
        Returns:
            bool: True если обновление успешно
        """
        self.stop_keep_alive()
        self._is_logged_in = False
        return self.login(username, password)

    def close(self):
        """Закрывает сессию и освобождает ресурсы"""
        self.stop_keep_alive()
        self._captcha_solver.close()
        self._request_client.close()
