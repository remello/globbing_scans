# collect_tracking_info.py

import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import re
from tracking_operations import login, get_package_info
from config import USERNAME, PASSWORD  # Убедитесь, что у вас есть файл config.py с вашими данными

def get_all_orders(session):
    base_url = 'https://kz.globbing.com/ru/profile/my-orders/received'
    orders = []
    limit = 100  # Можно увеличить при необходимости
    offset = 0
    while True:
        timestamp = int(time.time() * 1000)
        url = f"{base_url}?limit={limit}&offset={offset}&t={timestamp}"
        headers = {
            'Accept': '*/*',
            'Referer': base_url,
            'X-Requested-With': 'XMLHttpRequest'
        }
        response = session.get(url, headers=headers)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # Поиск всех строк с заказами
        rows = soup.select('table tbody tr')
        if not rows:
            break  # Если заказов больше нет, выходим из цикла

        for row in rows:
            tracking_number_element = row.select_one('.track-number__col--out a')
            if tracking_number_element:
                tracking_number = tracking_number_element.get('title')
                product_page_link = tracking_number_element.get('href')
                orders.append({
                    'tracking_number': tracking_number,
                    'product_page_link': product_page_link
                })
        offset += limit
    return orders

def extract_order_number_from_link(link):
    match = re.search(r'/(\d+)$', link)
    if match:
        return match.group(1)
    else:
        return None

def main():
    session = requests.Session()
    if not login(session, USERNAME, PASSWORD):
        print("Не удалось выполнить вход в систему")
        return
    print("Успешный вход в систему")

    orders = get_all_orders(session)
    print(f"Найдено {len(orders)} заказов")

    # Настройка базы данных
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_number TEXT PRIMARY KEY,
            tracking_number TEXT,
            weight TEXT,
            price_usd TEXT
        )
    ''')

    for order in orders:
        tracking_number = order['tracking_number']
        product_page_link = order['product_page_link']

        # Получение веса и стоимости
        weight, price_usd = get_package_info(session, product_page_link)

        # Извлечение номера заказа из ссылки
        order_number = extract_order_number_from_link(product_page_link)
        if not order_number:
            continue  # Пропускаем, если не удалось извлечь номер заказа

        # Сохранение данных в базе данных
        cursor.execute('''
            INSERT OR REPLACE INTO orders (order_number, tracking_number, weight, price_usd)
            VALUES (?, ?, ?, ?)
        ''', (order_number, tracking_number, weight, price_usd))

    conn.commit()
    conn.close()
    print("Данные успешно сохранены в базе данных")

main()
