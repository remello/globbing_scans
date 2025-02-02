import time
from typing import Optional
from selenium.webdriver.common.by import By
from ..exceptions import CaptchaError

class CaptchaSolver:
    """Класс для работы с reCAPTCHA через Selenium"""
    
    def __init__(self, selenium_driver):
        """
        Инициализация решателя капчи
        
        Args:
            selenium_driver: Инстанс Selenium WebDriver
        """
        self._driver = selenium_driver

    def get_token(self, url: str, wait_time: int = 20) -> str:
        """
        Получает reCAPTCHA токен через Selenium
        
        Args:
            url: URL страницы с капчей
            wait_time: Время ожидания загрузки капчи в секундах
            
        Returns:
            str: reCAPTCHA токен
            
        Raises:
            CaptchaError: При ошибке получения токена
        """
        try:
            self._driver.get(url)
            time.sleep(wait_time)  # Ждем загрузку страницы и reCAPTCHA
            
            recaptcha_input = self._driver.find_element(By.ID, 'g-recaptcha-response')
            token = recaptcha_input.get_attribute('value')
            
            if not token:
                raise CaptchaError("reCAPTCHA token is empty")
                
            return token
            
        except Exception as e:
            raise CaptchaError(f"Failed to get reCAPTCHA token: {str(e)}")
            
    def close(self):
        """Закрывает Selenium драйвер"""
        if self._driver:
            self._driver.quit()
            self._driver = None
