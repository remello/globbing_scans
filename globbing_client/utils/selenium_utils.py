from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def create_driver(headless: bool = True) -> webdriver.Chrome:
    """
    Создает и настраивает Chrome WebDriver
    
    Args:
        headless: Запускать браузер в фоновом режиме
        
    Returns:
        Chrome WebDriver с настроенными опциями
    """
    # Настройки Chrome
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")  # Новый headless режим
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")  # Установка размера окна
        chrome_options.add_argument("--disable-notifications")  # Отключение уведомлений
        chrome_options.add_argument("--disable-extensions")  # Отключение расширений

    # Автоматическое управление драйвером
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver
