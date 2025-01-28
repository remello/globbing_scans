import requests
from bs4 import BeautifulSoup
import time
import traceback

def search(session, search_request):
    """
    Поиск трек-номера с использованием сессии
    
    Args:
        session: Объект requests.Session для выполнения запросов
        search_request: Строка поиска (трек-номер)
        
    Returns:
        dict: Результат поиска с информацией о посылке или None в случае ошибки
    """
    try:
        # Формируем URL с параметрами поиска
        timestamp = int(time.time() * 1000)
        url = f"https://kz.globbing.com/ru/profile/my-orders/received?limit=50&search={search_request}&t={timestamp}"

        # Заголовки запроса
        headers = {
            'Accept': '*/*',
            'Referer': 'https://kz.globbing.com/ru/profile/my-orders/received',
            'X-Requested-With': 'XMLHttpRequest'
        }

        # Выполняем GET запрос
        response = session.get(url, headers=headers)
        response.raise_for_status()
        result = response.text

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(result, 'html.parser')

        # Find the tracking number and the link to the product page
        tracking_number_element = soup.select_one('.track-number__col--out a')
        if tracking_number_element:
            tracking_number = tracking_number_element.get('title')
            product_page_link = tracking_number_element.get('href')

            # Get the package info (weight and price)
            weight, price_usd = get_package_info(session, product_page_link)
            return {
                'tracking_number': tracking_number,
                'product_page_link': product_page_link,
                'weight': weight,
                'price_usd': price_usd,
                'raw_tracking_number': tracking_number_element.text.strip()  # Return raw tracking number
            }
        else:
            print("Tracking number or product page link not found.")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None

def fetch_page_content(session, product_page_link):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
        'Referer': 'https://kz.globbing.com/ru/profile/my-orders/received',
        # other headers as needed
    }

    response = session.get(product_page_link, headers=headers)
    response.raise_for_status()
    return response.text

def extract_weight_and_price_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the weight element
    weight_title = soup.find("p", class_="fs12", string="Вес")
    if weight_title:
        weight = weight_title.find_next("p", class_="fs14").text.strip()
    else:
        print("Weight title element not found.")
        weight = None

    # Find the price element
    price_element = soup.find("p", class_="fs12", string="Стоимость доставки")
    if price_element:
        price_usd = price_element.find_next("p", class_="fs14").text.strip()
    else:
        print("Price element not found.")
        price_usd = None

    return weight, price_usd

def get_package_info(session, product_page_link):
    try:
        # Fetch the page content
        result = fetch_page_content(session, product_page_link)
        
        if result:
            # Extract weight and price from the HTML content
            weight, price_usd = extract_weight_and_price_from_html(result)
            return weight, price_usd
        else:
            print("Error or unsuccessful request")
            return None, None

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None, None
