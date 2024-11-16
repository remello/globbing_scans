import tkinter as tk
from tkinter import messagebox
import logging
from tracking_operations import login, search
from tracking_info import finder
from config import USERNAME, PASSWORD, EXCHANGE_RATE  # Imported EXCHANGE_RATE
from logger import setup_logging
from messages import WEIGHT_AND_COST_MESSAGE, PAYMENT_MESSAGE
import requests
from translator import translate_rus_to_eng

class TrackingApp:
    def __init__(self, root):
        # Set up logging
        setup_logging()
        self.root = root
        self.session = requests.Session()  # Create a requests.Session object
        self.setup_ui()
        self.login()

    def login(self):
        if login(self.session, USERNAME, PASSWORD):
            print("Login successful")
        else:
            print("Login failed")

    def setup_ui(self):
        self.root.title("Tracking Number Input")
        self.root.attributes("-topmost", True)

        label = tk.Label(self.root, text="Enter Tracking Number:")
        label.pack(pady=10)

        entry_frame = tk.Frame(self.root)
        entry_frame.pack(pady=10)

        self.entry = tk.Entry(entry_frame, width=50)
        self.entry.pack(side=tk.LEFT, padx=5)
        self.entry.bind("<Return>", self.submit_tracking_number)
        self.entry.bind("<Control-v>", self.paste)  # Handler for pasting text
        self.entry.bind("<KeyRelease>", self.translate_input)  # Bind the translator

        self.clear_button = tk.Button(entry_frame, text="X", command=self.clear_entry)
        self.clear_button.pack(side=tk.LEFT)

        submit_button = tk.Button(self.root, text="Submit", command=self.submit_tracking_number)
        submit_button.pack(pady=10)

        # Display the entered tracking number under the entry field
        self.entered_tracking_number_label = tk.Label(self.root, text="")
        self.entered_tracking_number_label.pack(pady=5)

        self.weight_and_cost_label = tk.Label(self.root, text="")
        self.weight_and_cost_label.pack(pady=10)

        # Text field for normal tracking number
        self.tracking_number_text_field = tk.Text(self.root, height=1, width=60)
        self.tracking_number_text_field.pack(pady=10)
        self.tracking_number_text_field.config(state=tk.NORMAL)

        # Text field for raw tracking number
        self.raw_tracking_number_text_field = tk.Text(self.root, height=1, width=60)
        self.raw_tracking_number_text_field.pack(pady=10)
        self.raw_tracking_number_text_field.config(state=tk.NORMAL)

        self.copy_track_button = tk.Button(
            self.root, text="Copy Tracking Number", command=self.copy_tracking_number_to_clipboard
        )
        self.copy_track_button.pack(pady=10)

        self.copy_button = tk.Button(
            self.root, text="Copy Message", command=self.copy_message_to_clipboard
        )
        self.copy_button.pack(pady=10)

    def paste(self, event):
        try:
            self.entry.insert(tk.INSERT, self.root.clipboard_get())
        except tk.TclError:
            pass
        return "break"

    def translate_input(self, event):
        current_text = self.entry.get()
        translated_text = translate_rus_to_eng(current_text)
        if current_text != translated_text:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, translated_text)

    def submit_tracking_number(self, event=None):
        tracking_number = self.entry.get()
        if tracking_number:
            logging.info(f"Tracking number submitted: {tracking_number} ")
            self.entered_tracking_number_label.config(text=f"Entered Tracking Number: {tracking_number}")
            self.entry.delete(0, tk.END)  # Clear the entry field after submitting

            search_result = search(self.session, tracking_number)  # Use self.session here
            if search_result:
                product_page_link = search_result["product_page_link"]
                weight = search_result["weight"]
                price_usd = search_result.get("price_usd")
                raw_tracking_number = search_result["raw_tracking_number"]  # Get raw tracking number
                if weight:
                    print(f"Weight: {weight}")

                    weight_value = float(weight.split()[0].replace(",", "."))
                    cost = weight_value * 1470

                    # Include price in USD
                    if price_usd:
                        price_usd_value = float(price_usd[:-2].replace(",", "."))
                        price_rub = price_usd_value * EXCHANGE_RATE
                        price_text = f"Price: {price_usd} USD ({price_rub:.2f} руб.)"
                    else:
                        price_text = "Price not available"
                        price_rub = 0.0  # Default value if price not available

                    self.weight_and_cost_label.config(
                        text=WEIGHT_AND_COST_MESSAGE.format(weight=weight, cost=cost, price_usd=price_usd, price_rub=price_rub)
                    )

                    message = PAYMENT_MESSAGE.format(cost=cost)
                    self.message = message  # Save the message to an instance variable
                    logging.info(
                        f"Raw Tracking Number: {raw_tracking_number}, "
                        f"Processed Tracking Number: {tracking_number}, "
                        f"Weight: {weight}, Cost: {cost:.2f} руб., "
                        f"Price: {price_usd} USD ({price_rub:.2f} руб.), "
                        f"Link: {product_page_link}"
                    )
                    # Use finder to get the right tracking number
                    tracking_number_text = finder(search_result["tracking_number"])
                    if isinstance(tracking_number_text, (tuple, list)):
                        tracking_number_text = "".join(tracking_number_text)
                    elif tracking_number_text is None:
                        tracking_number_text = ""
                    self.tracking_number_text_field.config(state=tk.NORMAL)
                    self.tracking_number_text_field.delete(1.0, tk.END)
                    self.tracking_number_text_field.insert(
                        tk.END, tracking_number_text
                    )  # Display normal tracking number

                    self.raw_tracking_number_text_field.config(state=tk.NORMAL)
                    self.raw_tracking_number_text_field.delete(1.0, tk.END)
                    self.raw_tracking_number_text_field.insert(
                        tk.END, raw_tracking_number
                    )  # Display raw tracking number

                    # Change background to green for 0.5 seconds
                    self.tracking_number_text_field.config(bg="green")
                    self.raw_tracking_number_text_field.config(bg="green")
                    self.root.after(
                        500, lambda: self.tracking_number_text_field.config(bg="white")
                    )
                    self.root.after(
                        500, lambda: self.raw_tracking_number_text_field.config(bg="white")
                    )
                    self.copy_tracking_number_to_clipboard()

                else:
                    messagebox.showerror(
                        "Error", "Failed to find the weight element or tracking number"
                    )
            else:
                # If tracking number is not found on Globbing
                logging.info(f"Tracking number not found. Using finder for: {tracking_number}")
                tracking_number_text = finder(tracking_number)
                if tracking_number_text:
                    if isinstance(tracking_number_text, (tuple, list)):
                        tracking_number_text = "".join(tracking_number_text)
                    self.tracking_number_text_field.config(state=tk.NORMAL)
                    self.tracking_number_text_field.delete(1.0, tk.END)
                    self.tracking_number_text_field.insert(
                        tk.END, tracking_number_text
                    )  # Display tracking number from finder

                    # Change background to green for 0.5 seconds
                    self.tracking_number_text_field.config(bg="green")
                    self.root.after(
                        500, lambda: self.tracking_number_text_field.config(bg="white")
                    )
                    self.copy_tracking_number_to_clipboard()
                else:
                    messagebox.showerror(
                        "Error", "Failed to process the tracking number using finder."
                    )
        else:
            messagebox.showwarning("Input Error", "Please enter a tracking number")

    def clear_entry(self):
        self.entry.delete(0, tk.END)
        self.entry.focus()

    def copy_message_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.message)
        self.copy_button.config(text="Copied")
        self.root.after(1000, lambda: self.copy_button.config(text="Copy Message"))

    def copy_tracking_number_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(
            self.tracking_number_text_field.get("1.0", tk.END).strip()
        )
        self.copy_track_button.config(text="Copied")
        self.root.after(
            1000, lambda: self.copy_track_button.config(text="Copy Tracking Number")
        )
