from globbing_client import GlobbingClient
from globbing_client.utils import create_driver

def main():
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
            print("Успешный вход в систему")
            
            # Теперь можно использовать http клиент для запросов
            response = client.http.get("https://kz.globbing.com/ru/profile/my-orders")
            print("Статус запроса:", response.status_code)
            
            # Сессия поддерживается автоматически в фоновом режиме
            # Если нужно обновить сессию вручную:
            # client.refresh_session()
            
        else:
            print("Ошибка входа в систему")
            
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        
    finally:
        # Закрываем клиент и освобождаем ресурсы
        client.close()

if __name__ == "__main__":
    main()
