from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def create_driver(headless=False):
    # Настройки Chrome
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")  # Для предотвращения возможных ошибок в headless-режиме
        chrome_options.add_argument("--no-sandbox")  # Для работы в окружениях без GUI (например, Docker)
        chrome_options.add_argument("--disable-dev-shm-usage")  # Для повышения стабильности

    # Автоматическое управление драйвером
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver