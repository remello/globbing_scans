from bs4 import BeautifulSoup
import time
import logging
import traceback

class TrackingService:
    def __init__(self, request_wrapper):
        self.request_wrapper = request_wrapper

    def search_tracking(self, tracking_number):
        """
        Поиск трек-номера с использованием сессии
        
        Args:
            tracking_number: Строка поиска (трек-номер)
            
        Returns:
            dict: Результат поиска с информацией о посылке или None в случае ошибки
        """
        try:
            timestamp = int(time.time() * 1000)
            url = f"https://kz.globbing.com/ru/profile/my-orders/received?limit=50&search={tracking_number}&t={timestamp}"

            headers = {
                'Accept': '*/*',
                'Referer': 'https://kz.globbing.com/ru/profile/my-orders/received',
                'X-Requested-With': 'XMLHttpRequest'
            }

            response = self.request_wrapper.get(url, headers=headers)
            response.raise_for_status()
            
            tracking_info = self._parse_search_response(response.text)
            if tracking_info:
                package_info = self._get_package_info(tracking_info['product_page_link'])
                tracking_info.update(package_info)
                return tracking_info
            
            return None

        except Exception as e:
            logging.error(f"Error searching tracking number: {e}")
            traceback.print_exc()
            return None

    def _parse_search_response(self, html_content):
        """Извлекает информацию о трекинге из HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        tracking_element = soup.select_one('.track-number__col--out a')
        
        if not tracking_element:
            logging.info("Tracking number element not found")
            return None
            
        return {
            'tracking_number': tracking_element.get('title'),
            'product_page_link': tracking_element.get('href'),
            'raw_tracking_number': tracking_element.text.strip()
        }

    def _get_package_info(self, product_page_link):
        """Получает информацию о весе и стоимости посылки"""
        try:
            html_content = self._fetch_page_content(product_page_link)
            if not html_content:
                return {'weight': None, 'price_usd': None}
                
            return self._extract_weight_and_price(html_content)

        except Exception as e:
            logging.error(f"Error getting package info: {e}")
            traceback.print_exc()
            return {'weight': None, 'price_usd': None}

    def _fetch_page_content(self, product_page_link):
        """Загружает содержимое страницы с информацией о посылке"""
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'Referer': 'https://kz.globbing.com/ru/profile/my-orders/received'
        }

        response = self.request_wrapper.get(product_page_link, headers=headers)
        response.raise_for_status()
        return response.text

    def _extract_weight_and_price(self, html_content):
        """Извлекает вес и стоимость из HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        result = {'weight': None, 'price_usd': None}
        
        # Извлекаем вес
        weight_title = soup.find("p", class_="fs12", string="Вес")
        if weight_title:
            result['weight'] = weight_title.find_next("p", class_="fs14").text.strip()
        
        # Извлекаем стоимость
        price_element = soup.find("p", class_="fs12", string="Стоимость доставки")
        if price_element:
            result['price_usd'] = price_element.find_next("p", class_="fs14").text.strip()
            
        return result

    def process_tracking_number(self, tracking_number, finder_func):
        """
        Обрабатывает трек-номер, используя поиск или finder
        
        Args:
            tracking_number: Трек-номер для обработки
            finder_func: Функция для обработки трек-номера в случае неудачного поиска
            
        Returns:
            tuple: (tracking_info, tracking_number_text)
                tracking_info - информация о посылке или None
                tracking_number_text - обработанный трек-номер или None
        """
        search_result = self.search_tracking(tracking_number)
        
        if search_result and search_result.get('weight'):
            tracking_number_text = finder_func(search_result['tracking_number'])
            if isinstance(tracking_number_text, (tuple, list)):
                tracking_number_text = "".join(tracking_number_text)
            return search_result, tracking_number_text
            
        # Если поиск не удался, пробуем использовать finder
        tracking_number_text = finder_func(tracking_number)
        if tracking_number_text:
            if isinstance(tracking_number_text, (tuple, list)):
                tracking_number_text = "".join(tracking_number_text)
            return None, tracking_number_text
            
        return None, None
