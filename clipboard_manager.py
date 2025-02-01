class ClipboardManager:
    def __init__(self, root):
        self.root = root
        self._clipboard_text = None

    def copy_to_clipboard(self, text):
        """
        Копирует текст в буфер обмена
        
        Args:
            text: Текст для копирования
        """
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self._clipboard_text = text

    def paste_from_clipboard(self):
        """
        Получает текст из буфера обмена
        
        Returns:
            str: Текст из буфера обмена или None в случае ошибки
        """
        try:
            return self.root.clipboard_get()
        except:
            return None

    def get_last_copied(self):
        """
        Возвращает последний скопированный текст
        
        Returns:
            str: Последний скопированный текст или None
        """
        return self._clipboard_text
