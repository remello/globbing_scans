import requests
from bs4 import BeautifulSoup
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import traceback

def get_recaptcha_via_requests(url):
    try:
        response = requests.get(url, timeout=30)  # Timeout of 30 seconds
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        recaptcha_input = soup.find('input', {'id': 'g-recaptcha-response'})
        if recaptcha_input:
            return recaptcha_input.get('value')
        else:
            print('reCAPTCHA element not found via requests.')
            return None
    except Exception as e:
        print(f'Error requesting page via requests: {e}')
        return None

def get_recaptcha_via_selenium(url):
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get(url)
        time.sleep(20)  # Wait 20 seconds for full page load and dynamic content
        recaptcha_input = driver.find_element(By.ID, 'g-recaptcha-response')
        recaptcha_value = recaptcha_input.get_attribute('value')
        return recaptcha_value
    except Exception as e:
        print(f'Error requesting page via Selenium: {e}')
        traceback.print_exc()
        return None
    finally:
        if driver:
            driver.quit()

def get_recaptcha_value(url):
    # Attempt to get value via requests
    recaptcha_value = get_recaptcha_via_requests(url)
    if recaptcha_value:
        return recaptcha_value
    else:
        # If failed, try with Selenium
        return get_recaptcha_via_selenium(url)

def login(session, email, password):
    try:
        login_url = "https://kz.globbing.com/ru/login/"

        # Get reCAPTCHA value using get_recaptcha_value(url)
        recaptcha_value = get_recaptcha_value(login_url)
        if not recaptcha_value:
            print("Failed to get reCAPTCHA value")
            return False

        # Get the login page to retrieve the _token value
        response = session.get(login_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        token_input = soup.find('input', {'name': '_token'})
        if token_input:
            token = token_input.get('value')
        else:
            print("Failed to get _token value")
            return False

        # Prepare the login data
        data = {
            'email': email,
            'password': password,
            'g-recaptcha-response': recaptcha_value,
            '_token': token
        }

        # Prepare headers
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': login_url
        }

        # Perform login
        login_response = session.post(login_url, data=data, headers=headers)
        login_response.raise_for_status()

        # The response might be JSON or might redirect
        # Let's check the response
        try:
            json_data = login_response.json()
            if 'data' in json_data and json_data['data'].get('message') == 'globbing.login.success':
                redirect_url = json_data['data'].get('redirect_url', 'https://kz.globbing.com/ru')
                # Optionally, follow the redirect
                session.get(redirect_url)
                return True
            else:
                print("Login failed:", json_data)
                return False
        except ValueError:
            # Response is not JSON, maybe the login was successful
            if login_response.url != login_url:
                # Redirected to another page, login successful
                return True
            else:
                print("Login failed, no JSON response")
                return False

    except Exception as e:
        print(f"An error occurred during login: {e}")
        traceback.print_exc()
        return False

def search(session, search_request):
    try:
        # Construct the URL with the request
        timestamp = int(time.time() * 1000)
        url = f"https://kz.globbing.com/ru/profile/my-orders/received?limit=50&search={search_request}&t={timestamp}"

        # Set the headers
        headers = {
            'Accept': '*/*',
            'Referer': 'https://kz.globbing.com/ru/profile/my-orders/received',
            'X-Requested-With': 'XMLHttpRequest'
            # Other headers as needed
        }

        # Perform GET request
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
