from bs4 import BeautifulSoup
import time
import traceback
import threading
import requests
from request_wrapper import RequestWrapper
from selenium_driver import create_driver
from selenium.webdriver.common.by import By

class GlobbingSession:
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._request_wrapper = RequestWrapper()
        self._session = self._request_wrapper.get_session()
        self._selenium_driver = None
        self._is_logged_in = False
        self._keep_alive_thread = None
        self._stop_keep_alive = threading.Event()
        
    def get(self):
        """Возвращает текущую сессию"""
        return self._session

    def _keep_alive(self):
        """Фоновый поток для поддержания сессии активной"""
        while not self._stop_keep_alive.is_set():
            try:
                if self._is_logged_in:
                    # Делаем запрос к профилю пользователя для поддержания сессии
                    self._request_wrapper.get("https://kz.globbing.com/ru/profile/my-orders")
            except Exception as e:
                print(f"Ошибка в keep_alive: {e}")
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
        
    def refresh(self):
        """Выполняет повторную авторизацию"""
        self.stop_keep_alive()
        new_session = requests.Session()
        self._session = new_session
        self._request_wrapper.set_session(new_session)
        if self._selenium_driver:
            self._selenium_driver.quit()
        self._selenium_driver = None
        success = self._login()
        if success:
            self.start_keep_alive()
        return success
        
    def _get_recaptcha_token(self, login_url):
        """Получает reCAPTCHA токен через Selenium"""
        try:
            # Закрываем предыдущую сессию Selenium, если она существует
            if self._selenium_driver:
                self._selenium_driver.quit()
                self._selenium_driver = None
                
            # Создаем новую сессию
            self._selenium_driver = create_driver()
            self._selenium_driver.get(login_url)
            time.sleep(20)  # Ждем загрузку страницы и reCAPTCHA
            recaptcha_input = self._selenium_driver.find_element(By.ID, 'g-recaptcha-response')
            token = recaptcha_input.get_attribute('value')
            
            # Закрываем сессию после получения токена
            self._selenium_driver.quit()
            self._selenium_driver = None
            
            return token
        except Exception as e:
            print(f'Ошибка получения reCAPTCHA токена: {e}')
            traceback.print_exc()
            if self._selenium_driver:
                self._selenium_driver.quit()
                self._selenium_driver = None
            return None
        
    def _login(self):
        """Выполняет авторизацию с использованием Selenium для reCAPTCHA"""
        try:
            login_url = "https://kz.globbing.com/ru/login/"
            
            # Получаем reCAPTCHA токен
            recaptcha_value = self._get_recaptcha_token(login_url)
            if not recaptcha_value:
                print("Не удалось получить reCAPTCHA токен")
                return False

            # Получаем _token со страницы логина
            response = self._request_wrapper.get(login_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            token_input = soup.find('input', {'name': '_token'})
            if not token_input:
                print("Не удалось получить _token")
                return False
            token = token_input.get('value')

            # Подготавливаем данные для авторизации
            data = {
                'email': self._username,
                'password': self._password,
                'g-recaptcha-response': recaptcha_value,
                '_token': token
            }

            # Заголовки запроса
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': login_url
            }

            # Выполняем авторизацию
            login_response = self._request_wrapper.post(login_url, data=data, headers=headers)

            # Проверяем ответ
            try:
                json_data = login_response.json()
                if 'data' in json_data and json_data['data'].get('message') == 'globbing.login.success':
                    redirect_url = json_data['data'].get('redirect_url', 'https://kz.globbing.com/ru')
                    self._request_wrapper.get(redirect_url)
                    self._is_logged_in = True
                    self.start_keep_alive()
                    return True
                else:
                    print("Ошибка авторизации:", json_data)
                    return False
            except ValueError:
                # Если ответ не JSON, проверяем редирект
                if login_response.url != login_url:
                    self._is_logged_in = True
                    self.start_keep_alive()
                    return True
                else:
                    print("Ошибка авторизации, нет JSON ответа")
                    return False

        except Exception as e:
            print(f"Ошибка при авторизации: {e}")
            traceback.print_exc()
            return False
            
    def __del__(self):
        """Закрываем Selenium драйвер и останавливаем фоновый поток при уничтожении объекта"""
        self.stop_keep_alive()
        if self._selenium_driver:
            self._selenium_driver.quit()
