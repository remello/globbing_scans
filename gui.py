import tkinter as tk
import logging
from tracking_info import finder
from config import USERNAME, PASSWORD, EXCHANGE_RATE
from cost_calculator import CostCalculator
from logger import setup_logging
from messages import WEIGHT_AND_COST_MESSAGE, PAYMENT_MESSAGE
from session import GlobbingSession
from translator import translate_rus_to_eng
from tracking_service import TrackingService
from price_service import PriceService
from ui_manager import UIManager
from clipboard_manager import ClipboardManager

class TrackingApp:
    def __init__(self, root):
        setup_logging()
        self.root = root
        
        # Инициализация сервисов
        self.session = GlobbingSession(USERNAME, PASSWORD)
        self.tracking_service = TrackingService(self.session.request_wrapper)
        self.price_service = PriceService(EXCHANGE_RATE)
        self.cost_calculator = CostCalculator()
        
        # Инициализация менеджеров
        self.ui_manager = UIManager(root)
        self.clipboard_manager = ClipboardManager(root)
        
        # Инициализация сообщения
        self.message = None
        
        self.setup_ui()
        self._login()

    def _login(self):
        """Вход в систему"""
        if self.session._login():
            logging.info("Login successful")
        else:
            logging.error("Login failed")
            self.ui_manager.show_error("Login Error", "Failed to login")

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Настройка поля ввода трек-номера
        self.ui_manager.setup_tracking_input(
            self.submit_tracking_number,
            self.paste,
            self.translate_input
        )
        
        # Настройка отображения информации
        self.ui_manager.setup_tracking_display()
        
        # Настройка кнопок копирования
        self.ui_manager.setup_copy_buttons(
            self.copy_tracking_number_to_clipboard,
            self.copy_message_to_clipboard
        )
        
        # Настройка модификатора стоимости
        self.ui_manager.setup_cost_modifier(
            self.cost_calculator.weight_cost_modifier,
            self.update_cost_modifier
        )

    def paste(self, event):
        """Обработчик вставки из буфера обмена"""
        text = self.clipboard_manager.paste_from_clipboard()
        if text:
            self.ui_manager.widgets['entry'].insert(tk.INSERT, text)
        return "break"

    def translate_input(self, event):
        """Обработчик перевода текста"""
        current_text = self.ui_manager.get_entry_text()
        translated_text = translate_rus_to_eng(current_text)
        if current_text != translated_text:
            entry = self.ui_manager.widgets['entry']
            entry.delete(0, tk.END)
            entry.insert(0, translated_text)

    def submit_tracking_number(self, event=None):
        """Обработка отправки трек-номера"""
        tracking_number = self.ui_manager.get_entry_text()
        if not tracking_number:
            self.ui_manager.show_warning("Input Error", "Please enter a tracking number")
            return

        logging.info(f"Tracking number submitted: {tracking_number}")
        self.ui_manager.update_tracking_label(f"Entered Tracking Number: {tracking_number}")
        self.ui_manager.widgets['entry'].delete(0, tk.END)

        # Получаем информацию о посылке
        tracking_info, tracking_number_text = self.tracking_service.process_tracking_number(
            tracking_number, finder
        )

        if tracking_info and tracking_info.get('weight'):
            self._handle_successful_search(tracking_info, tracking_number_text)
        elif tracking_number_text:
            self._handle_finder_only(tracking_number_text)
        else:
            self.ui_manager.show_error(
                "Error", "Failed to process the tracking number."
            )

    def _handle_successful_search(self, tracking_info, tracking_number_text):
        """Обработка успешного поиска"""
        weight = tracking_info['weight']
        price_usd = tracking_info.get('price_usd')
        raw_tracking_number = tracking_info['raw_tracking_number']

        # Расчет стоимости
        cost = self.cost_calculator.calculate_cost(weight)

        # Форматирование цены
        price_text, price_rub = self.price_service.format_price(price_usd)

        # Обновление UI
        self.ui_manager.update_weight_cost_label(
            WEIGHT_AND_COST_MESSAGE.format(
                weight=weight, cost=cost, 
                price_usd=price_usd, price_rub=price_rub
            )
        )

        # Сохранение сообщения для копирования
        self.message = PAYMENT_MESSAGE.format(cost=cost)

        # Логирование
        logging.info(
            f"Raw Tracking Number: {raw_tracking_number}, "
            f"Processed Tracking Number: {tracking_number_text}, "
            f"Weight: {weight}, Cost: {cost:.2f} руб., "
            f"Price: {price_usd} USD ({price_rub:.2f} руб.), "
            f"Link: {tracking_info['product_page_link']}"
        )

        # Обновление полей с трек-номерами
        self.ui_manager.update_tracking_fields(
            tracking_number_text or "",
            raw_tracking_number
        )
        
        # Копируем трек-номер
        self.copy_tracking_number_to_clipboard()

    def _handle_finder_only(self, tracking_number_text):
        """Обработка случая, когда сработал только finder"""
        self.ui_manager.update_tracking_fields(tracking_number_text, "")
        self.copy_tracking_number_to_clipboard()

    def copy_message_to_clipboard(self):
        """Копирование сообщения в буфер обмена"""
        self.clipboard_manager.copy_to_clipboard(self.message)
        self.ui_manager.update_copy_button_text('copy_message_button', "Copied")

    def copy_tracking_number_to_clipboard(self):
        """Копирование трек-номера в буфер обмена"""
        tracking_number = self.ui_manager.get_tracking_field_text()
        self.clipboard_manager.copy_to_clipboard(tracking_number)
        self.ui_manager.update_copy_button_text('copy_track_button', "Copied")

    def update_cost_modifier(self):
        """Обновление модификатора стоимости"""
        try:
            new_value = self.ui_manager.get_cost_modifier_value()
            self.cost_calculator.weight_cost_modifier = float(new_value)
            self.ui_manager.show_info(
                "Успех", 
                f"Модификатор стоимости обновлен: {new_value}"
            )
        except ValueError as e:
            self.ui_manager.show_error("Ошибка", str(e))
