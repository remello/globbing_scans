# Globbing Client Library

Библиотека для работы с API Globbing с поддержкой автоматической авторизации и управления сессией.

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd globbing-client
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Использование

### Базовый пример

```python
from globbing_client import GlobbingClient
from globbing_client.utils import create_driver

# Создаем Selenium драйвер
driver = create_driver()

try:
    # Инициализируем клиент
    client = GlobbingClient(
        username="your_username",
        password="your_password",
        selenium_driver=driver
    )
    
    # Выполняем вход
    if client.login():
        # Делаем запросы через http клиент
        response = client.http.get("https://kz.globbing.com/ru/profile/my-orders")
        print(response.status_code)
finally:
    # Закрываем клиент
    client.close()
```

### Особенности

- Автоматическая обработка reCAPTCHA при авторизации
- Автоматическое поддержание сессии активной
- Повторные попытки при ошибках HTTP запросов
- Корректное освобождение ресурсов

### Компоненты

- `GlobbingClient` - Основной класс для работы с API
- `RequestClient` - HTTP клиент с поддержкой повторных попыток
- `SessionManager` - Управление сессией и авторизацией
- `CaptchaSolver` - Работа с reCAPTCHA через Selenium

## Зависимости

- Python 3.7+
- selenium >= 4.0.0
- beautifulsoup4 >= 4.9.0
- requests >= 2.25.0
- webdriver-manager >= 3.8.0

## Лицензия

MIT
