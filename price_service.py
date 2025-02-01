class PriceService:
    def __init__(self, exchange_rate):
        self.exchange_rate = exchange_rate

    def convert_to_rub(self, usd_price_str):
        """
        Конвертирует цену из USD в рубли
        
        Args:
            usd_price_str: Строка с ценой в USD (например, "10.5 USD")
            
        Returns:
            tuple: (float, float) - (цена в USD, цена в рублях)
            или (0.0, 0.0) в случае ошибки
        """
        try:
            if not usd_price_str:
                return 0.0, 0.0
                
            # Извлекаем числовое значение из строки
            usd_value = float(usd_price_str[:-2].replace(",", "."))
            rub_value = usd_value * self.exchange_rate
            
            return usd_value, rub_value
            
        except (ValueError, IndexError):
            return 0.0, 0.0

    def format_price(self, usd_price_str):
        """
        Форматирует цену для отображения
        
        Args:
            usd_price_str: Строка с ценой в USD
            
        Returns:
            tuple: (str, float) - (отформатированный текст цены, цена в рублях)
        """
        usd_value, rub_value = self.convert_to_rub(usd_price_str)
        
        if usd_value > 0:
            return f"Price: {usd_price_str} USD ({rub_value:.2f} руб.)", rub_value
        else:
            return "Price not available", 0.0
