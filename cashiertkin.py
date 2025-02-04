import tkinter as tk
from tkinter import ttk
from collections import defaultdict
from PIL import Image, ImageTk, ImageEnhance  # Added ImageEnhance for brightness adjustments

class CashierCheckout:
    def __init__(self):
        # Initialize detected objects
        self.detected_objects = defaultdict(lambda: {'count': 0, 'total': 0})  # Track detected items
        self.prices = {
            "apple": 1.99,
            "banana": 2.9,
            "orange": 3.99,
        }
        # Example items for testing
        self.detected_objects['apple']['count'] = 2
        self.detected_objects['apple']['total'] = 2 * self.prices['apple']
        self.detected_objects['banana']['count'] = 3
        self.detected_objects['banana']['total'] = 3 * self.prices['banana']

        # Calculate total price
        self.total_price = sum(data['total'] for data in self.detected_objects.values())

        # Load the QR code, Cash, and Buy Me a Coffee images (to be done in separate methods)
        self.qr_code_image = None
        self.cash_image = None
        self.buymeacoffee_image = None
        self.original_qr_image = None
        self.original_cash_image = None

    def load_qr_code_image(self):
        try:
            img = Image.open("qrcode.jpg")  # Adjust the path if necessary
            img = img.resize((250, 200), Image.Resampling.LANCZOS)  # Resize the image to fit the frame
            self.qr_code_image = ImageTk.PhotoImage(img)
            self.original_qr_image = img  # Store the original image
        except Exception as e:
            print(f"Error loading QR code image: {e}")

    def load_cash_image(self):
        try:
            img = Image.open("cash.jpg")  # Adjust the path if necessary
            img = img.resize((250, 200), Image.Resampling.LANCZOS)  # Resize the image to fit the frame
            self.cash_image = ImageTk.PhotoImage(img)
            self.original_cash_image = img  # Store the original image
        except Exception as e:
            print(f"Error loading cash image: {e}")

    def load_buymeacoffee_image(self):
        try:
            img = Image.open("buymeacoffee.jpg")  # Adjust the path if necessary
            img = img.resize((400, 400), Image.Resampling.LANCZOS)  # Resize the image to a larger size
            self.buymeacoffee_image = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading Buy Me a Coffee image: {e}")

    def darken_qr_image(self):
        enhancer = ImageEnhance.Brightness(self.original_qr_image)
        darkened_img = enhancer.enhance(0.5)  # Darken the image
        self.qr_code_image = ImageTk.PhotoImage(darkened_img)
        return self.qr_code_image

    def restore_qr_image(self):
        self.qr_code_image = ImageTk.PhotoImage(self.original_qr_image)
        return self.qr_code_image

    def darken_cash_image(self):
        enhancer = ImageEnhance.Brightness(self.original_cash_image)
        darkened_img = enhancer.enhance(0.5)  # Darken the image
        self.cash_image = ImageTk.PhotoImage(darkened_img)
        return self.cash_image

    def restore_cash_image(self):
        self.cash_image = ImageTk.PhotoImage(self.original_cash_image)
        return self.cash_image

    def display_price_window(self):
        self.tk_window = tk.Tk()
        self.tk_window.title("Cashier Checkout")
        self.tk_window.attributes("-fullscreen", True)
        self.tk_window.configure(bg="#F8F9F0")  # Light gray background

        title_label = tk.Label(self.tk_window, text="Cashier Checkout", font=("Helvetica", 40, "bold"), bg="#F8F9F0", fg="#333333")
        title_label.pack(pady=20)

        frame = tk.Frame(self.tk_window, bg="#FFFFFF", bd=2, relief="raised")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        separator = ttk.Separator(self.tk_window, orient="horizontal")
        separator.pack(fill="x", padx=20)

        # Load the images
        self.load_qr_code_image()
        self.load_cash_image()

        columns = ("Item", "Price", "Quantity", "Total")
        item_list = ttk.Treeview(frame, columns=columns, show='headings', height=10)

        item_list.heading("Item", text="Item")
        item_list.heading("Price", text="Price ($)")
        item_list.heading("Quantity", text="Quantity")
        item_list.heading("Total", text="Total ($)")

        item_list.column("Item", width=300, anchor="center")
        item_list.column("Price", width=200, anchor="center")
        item_list.column("Quantity", width=200, anchor="center")
        item_list.column("Total", width=200, anchor="center")

        style = ttk.Style()
        style.configure("Treeview", font=("Helvetica", 18), rowheight=40)
        style.configure("Treeview.Heading", font=("Helvetica", 24, "bold"))

        for item_name, data in self.detected_objects.items():
            price = self.prices.get(item_name.lower(), 0)
            count = data['count']
            total_for_item = data['total']
            item_list.insert("", "end", values=(item_name.capitalize(), f"{price:.2f}", count, f"{total_for_item:.2f}"))

        item_list.pack(fill="both", expand=True)

        total_price_text = f"Total Price: ${self.total_price:.2f}"
        total_price_label = tk.Label(frame, text=total_price_text, font=("Helvetica", 28, "bold"), bg="#FFFFFF", fg="#D9534F")
        total_price_label.pack(pady=20)

        button_frame = tk.Frame(self.tk_window, bg="#F8F9F0")
        button_frame.pack(pady=20)

        retry_button = ttk.Button(button_frame, text="Retry", command=self.retry_action, style="Accent.TButton")
        retry_button.grid(row=0, column=0, padx=20, pady=10)

        quit_button = ttk.Button(button_frame, text="Quit", command=self.close_cashier_checkout, style="Accent.TButton")
        quit_button.grid(row=0, column=1, padx=20, pady=10)

        checkout_button = ttk.Button(button_frame, text="Checkout", command=self.checkout_action, style="Accent.TButton")
        checkout_button.grid(row=0, column=2, padx=20, pady=10)

        style.configure("Accent.TButton", font=("Helvetica", 18, "bold"), padding=10)
        style.map("Accent.TButton", foreground=[('active', '#FFFFFF')], background=[('active', '#D9534F')])

        self.tk_window.mainloop()

    def checkout_action(self):
        checkout_window = tk.Toplevel(self.tk_window)
        checkout_window.title("Checkout Confirmation")
        checkout_window.geometry("600x500")

        price_label = tk.Label(checkout_window, text=f"Total Price: ${self.total_price:.2f}", font=("Helvetica", 30, "bold"), fg="#D9534F")
        price_label.pack(pady=20)

        paymentmethod_label = tk.Label(checkout_window, text=f'Select Payment Method', font=("Helvetica", 30, "bold"))
        paymentmethod_label.pack(pady=5)

        boxes_frame = tk.Frame(checkout_window)
        boxes_frame.pack(pady=20)

        qr_label = tk.Label(boxes_frame, text="QR Code", font=("Helvetica", 16, "bold"))
        qr_label.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="s")

        cash_label = tk.Label(boxes_frame, text="Cashout", font=("Helvetica", 16, "bold"))
        cash_label.grid(row=0, column=1, padx=10, pady=(0, 10), sticky="s")

        def on_enter_qr(event):
            qr_image_label.config(image=self.darken_qr_image())  # Change the image to a darker one

        def on_leave_qr(event):
            qr_image_label.config(image=self.restore_qr_image())  # Restore the original image

        def on_enter_cash(event):
            cash_image_label.config(image=self.darken_cash_image())  # Change the image to a darker one

        def on_leave_cash(event):
            cash_image_label.config(image=self.restore_cash_image())  # Restore the original image

        qr_frame = tk.Frame(boxes_frame, width=250, height=200, bd=2, relief="raised", bg="#FFFFFF")
        qr_frame.grid(row=1, column=0, padx=10)

        cash_frame = tk.Frame(boxes_frame, width=250, height=200, bd=2, relief="raised", bg="#FFFFFF")
        cash_frame.grid(row=1, column=1, padx=10)

        if self.qr_code_image:
            qr_image_label = tk.Label(qr_frame, image=self.qr_code_image, bg="#FFFFFF")
            qr_image_label.pack(fill="both", expand=True)
            qr_frame.bind("<Enter>", on_enter_qr)
            qr_frame.bind("<Leave>", on_leave_qr)
            qr_image_label.bind("<Button-1>", self.qr_clicked)  # Bind click event to the QR image

        if self.cash_image:
            cash_image_label = tk.Label(cash_frame, image=self.cash_image, bg="#FFFFFF")
            cash_image_label.pack(fill="both", expand=True)
            cash_frame.bind("<Enter>", on_enter_cash)
            cash_frame.bind("<Leave>", on_leave_cash)
            cash_image_label.bind("<Button-1>", self.cash_clicked)  # Bind click event to the cash image

    def qr_clicked(self, event):
        # Create a new window on click
        new_window = tk.Toplevel(self.tk_window)
        new_window.title("QR Code Clicked")
        new_window.geometry("600x600")  # Increased window size

        label = tk.Label(new_window, text="QR Code Clicked!", font=("Helvetica", 24))
        label.pack(pady=20)

        # Load and display the Buy Me a Coffee image
        self.load_buymeacoffee_image()  # Ensure the image is loaded
        if self.buymeacoffee_image:
            coffee_image_label = tk.Label(new_window, image=self.buymeacoffee_image)
            coffee_image_label.pack(pady=10)

        close_button = ttk.Button(new_window, text="Close", command=new_window.destroy)
        close_button.pack(pady=20)

    def cash_clicked(self, event):
        # Handle cash clicked event
        print("Cash clicked!")

    def retry_action(self):
        if hasattr(self, 'tk_window') and self.tk_window.winfo_exists():
            self.tk_window.destroy()

    def close_cashier_checkout(self):
        if hasattr(self, 'tk_window') and self.tk_window.winfo_exists():
            self.tk_window.destroy()


if __name__ == "__main__":
    cashier = CashierCheckout()
    cashier.display_price_window()
