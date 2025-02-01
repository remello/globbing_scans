import tkinter as tk
from tkinter import messagebox

class UIManager:
    def __init__(self, root):
        self.root = root
        self.widgets = {}
        self._setup_window()

    def _setup_window(self):
        """Настройка основного окна"""
        self.root.title("Tracking Number Input")
        self.root.attributes("-topmost", True)

    def setup_tracking_input(self, submit_callback, paste_callback, translate_callback):
        """Создание элементов для ввода трек-номера"""
        label = tk.Label(self.root, text="Enter Tracking Number:")
        label.pack(pady=10)

        entry_frame = tk.Frame(self.root)
        entry_frame.pack(pady=10)

        entry = tk.Entry(entry_frame, width=50)
        entry.pack(side=tk.LEFT, padx=5)
        entry.bind("<Return>", submit_callback)
        entry.bind("<Control-v>", paste_callback)
        entry.bind("<KeyRelease>", translate_callback)
        
        clear_button = tk.Button(entry_frame, text="X", 
                               command=lambda: self.clear_entry(entry))
        clear_button.pack(side=tk.LEFT)

        submit_button = tk.Button(self.root, text="Submit", 
                                command=lambda: submit_callback(None))
        submit_button.pack(pady=10)

        self.widgets['entry'] = entry
        return entry

    def setup_tracking_display(self):
        """Создание элементов для отображения информации о трекинге"""
        # Метка для отображения введенного трек-номера
        tracking_label = tk.Label(self.root, text="")
        tracking_label.pack(pady=5)

        # Метка для отображения веса и стоимости
        weight_cost_label = tk.Label(self.root, text="")
        weight_cost_label.pack(pady=10)

        # Поле для нормального трек-номера
        tracking_field = tk.Text(self.root, height=1, width=60)
        tracking_field.pack(pady=10)
        tracking_field.config(state=tk.NORMAL)

        # Поле для исходного трек-номера
        raw_tracking_field = tk.Text(self.root, height=1, width=60)
        raw_tracking_field.pack(pady=10)
        raw_tracking_field.config(state=tk.NORMAL)

        self.widgets.update({
            'tracking_label': tracking_label,
            'weight_cost_label': weight_cost_label,
            'tracking_field': tracking_field,
            'raw_tracking_field': raw_tracking_field
        })

    def setup_copy_buttons(self, copy_track_callback, copy_message_callback):
        """Создание кнопок копирования"""
        copy_track_button = tk.Button(
            self.root, text="Copy Tracking Number", command=copy_track_callback
        )
        copy_track_button.pack(pady=10)

        copy_message_button = tk.Button(
            self.root, text="Copy Message", command=copy_message_callback
        )
        copy_message_button.pack(pady=10)

        self.widgets.update({
            'copy_track_button': copy_track_button,
            'copy_message_button': copy_message_button
        })

    def setup_cost_modifier(self, initial_value, save_callback):
        """Создание элементов для модификатора стоимости"""
        cost_frame = tk.Frame(self.root)
        cost_frame.pack(pady=5)
        
        cost_label = tk.Label(cost_frame, text="Модификатор стоимости:")
        cost_label.pack(side=tk.LEFT, padx=5)
        
        cost_entry = tk.Entry(cost_frame, width=10)
        cost_entry.insert(0, str(initial_value))
        cost_entry.pack(side=tk.LEFT, padx=5)
        
        save_button = tk.Button(cost_frame, text="Сохранить", 
                              command=lambda: save_callback())
        save_button.pack(side=tk.LEFT, padx=5)

        self.widgets['cost_entry'] = cost_entry

    def clear_entry(self, entry):
        """Очистка поля ввода"""
        entry.delete(0, tk.END)
        entry.focus()

    def update_tracking_label(self, text):
        """Обновление метки с трек-номером"""
        self.widgets['tracking_label'].config(text=text)

    def update_weight_cost_label(self, text):
        """Обновление метки с весом и стоимостью"""
        self.widgets['weight_cost_label'].config(text=text)

    def update_tracking_fields(self, tracking_text, raw_tracking_text):
        """Обновление полей с трек-номерами"""
        # Обновляем обычный трек-номер
        field = self.widgets['tracking_field']
        field.config(state=tk.NORMAL)
        field.delete(1.0, tk.END)
        field.insert(tk.END, tracking_text)
        
        # Обновляем исходный трек-номер
        raw_field = self.widgets['raw_tracking_field']
        raw_field.config(state=tk.NORMAL)
        raw_field.delete(1.0, tk.END)
        raw_field.insert(tk.END, raw_tracking_text)

        # Подсветка зеленым на 0.5 секунд
        field.config(bg="green")
        raw_field.config(bg="green")
        self.root.after(500, lambda: field.config(bg="white"))
        self.root.after(500, lambda: raw_field.config(bg="white"))

    def get_entry_text(self):
        """Получение текста из поля ввода"""
        return self.widgets['entry'].get()

    def get_cost_modifier_value(self):
        """Получение значения модификатора стоимости"""
        return self.widgets['cost_entry'].get()

    def get_tracking_field_text(self):
        """Получение текста из поля трек-номера"""
        return self.widgets['tracking_field'].get("1.0", tk.END).strip()

    def show_error(self, title, message):
        """Отображение сообщения об ошибке"""
        messagebox.showerror(title, message)

    def show_warning(self, title, message):
        """Отображение предупреждения"""
        messagebox.showwarning(title, message)

    def show_info(self, title, message):
        """Отображение информационного сообщения"""
        messagebox.showinfo(title, message)

    def update_copy_button_text(self, button_name, text):
        """Обновление текста кнопки копирования"""
        self.widgets[button_name].config(text=text)
        self.root.after(1000, lambda: self.widgets[button_name].config(
            text="Copy Tracking Number" if button_name == 'copy_track_button' else "Copy Message"
        ))
