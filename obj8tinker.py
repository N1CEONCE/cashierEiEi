import cv2
import threading
import numpy as np
from collections import defaultdict
from ultralytics import YOLO
import tkinter as tk
from tkinter import ttk

class MobileCamera:
    def __init__(self):
        # Load YOLOv8 model for object detection
        self.model = YOLO('yolov8n.pt')  # Use 'yolov8n.pt' or any desired model
        self.frame = None
        self.running = True
        self.frame_skip = 0  # Initialize frame skip
        self.photo_count = 0  # To count the saved photos
        self.total_price = 0  # To accumulate the total price
        self.detected_objects = defaultdict(lambda: {'count': 0, 'total': 0})  # Track each object and its total cost
        self.show_price_window = False  # Flag to control the display of the price window

        # Dictionary to store prices for specific object classes
        self.prices = {
            "apple": 1,  # Price of an apple is $1
            "banana": 2,  # Price of a banana is $2
            "orange": 3,  # Price of an orange is $3
            # Add more object types and their prices here
        }

    def getVideo(self, camera):
        self.camera = camera
        cap = cv2.VideoCapture(self.camera)

        # Reduce resolution to 640x480
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # Function to capture frames in a separate thread
        def capture_frames():
            while self.running:
                ret, frame = cap.read()
                if ret:
                    self.frame = frame

        # Start a thread to capture frames
        thread = threading.Thread(target=capture_frames)
        thread.start()

        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                # Check if the "Scan" button was clicked
                if 30 < x < 150 and 30 < y < 80:
                    self.capture_photo()  # Call the function to handle 'c'

                # Check if the "Retry" button was clicked
                if 180 < x < 300 and 30 < y < 80:
                    self.retry_action()  # Call the function to handle 'e'

                # Check if the "Quit" button was clicked
                if 330 < x < 450 and 30 < y < 80:
                    self.quit_action()  # Call the function to handle 'q'

        # Set the mouse callback function for the window
        cv2.namedWindow("Mobile Cam - Object Detection")
        cv2.setMouseCallback("Mobile Cam - Object Detection", mouse_callback)

        while True:
            if self.frame is not None:
                # Skip every 2nd frame to reduce processing load
                if self.frame_skip % 2 == 0:
                    # Detect objects using YOLOv8 model
                    results = self.model(self.frame)

                    # Reset detected objects and total price for this frame
                    self.detected_objects.clear()
                    self.total_price = 0

                    # Loop over detected objects
                    for result in results:
                        boxes = result.boxes
                        for box in boxes:
                            # Extract bounding box and confidence score
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            conf = box.conf[0]
                            cls = int(box.cls[0])

                            # Only show results with high confidence
                            if conf > 0.5:  # Threshold for confidence
                                # Draw rectangle for detected object
                                cv2.rectangle(self.frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

                                # Get object class name from YOLO
                                class_name = self.model.names[cls]

                                # Get price from the price dictionary
                                price_tag = self.prices.get(class_name.lower(),
                                                            10)  # Default price is 10 if the object is not in the dictionary

                                # Display class name and price tag on the video frame
                                cv2.putText(self.frame, f"{class_name}: ${price_tag}",
                                            (x1, y1 - 10),
                                            cv2.FONT_HERSHEY_SIMPLEX,
                                            1,  # Larger font scale for price display
                                            (0, 255, 0),
                                            2)  # Thicker font for better readability

                                # Add the object, increment count and calculate total for each type
                                self.detected_objects[class_name]['count'] += 1
                                self.detected_objects[class_name]['total'] = self.detected_objects[class_name][
                                                                                 'count'] * price_tag

                    # Calculate the cumulative total price for all detected items
                    self.total_price = sum(item['total'] for item in self.detected_objects.values())

                    # Draw buttons for "Scan", "Retry", and "Quit"
                    self.draw_buttons(self.frame)

                    # Display the frame with object detection
                    cv2.imshow("Mobile Cam - Object Detection", self.frame)

                self.frame_skip += 1

            # Capture keyboard input for 'c', 'e', and 'q'
            key = cv2.waitKey(1)
            if key == ord('c'):  # Scan (same as clicking "Scan")
                self.capture_photo()
            elif key == ord('e'):  # Retry (same as clicking "Retry")
                self.retry_action()
            elif key == ord('q'):  # Quit (same as clicking "Quit")
                self.quit_action()
                break

        cap.release()
        thread.join()
        cv2.destroyAllWindows()

    def draw_buttons(self, frame):
        # Draw "Scan" button
        cv2.rectangle(frame, (30, 30), (150, 80), (200, 200, 200), -1)
        cv2.putText(frame, "Scan", (50, 65), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        # Draw "Retry" button
        cv2.rectangle(frame, (180, 30), (300, 80), (200, 200, 200), -1)
        cv2.putText(frame, "Retry", (200, 65), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        # Draw "Quit" button
        cv2.rectangle(frame, (330, 30), (450, 80), (200, 200, 200), -1)
        cv2.putText(frame, "Quit", (350, 65), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    def capture_photo(self):
        # Save the current frame as an image
        if self.frame is not None:
            photo_name = f"detected_photo_{self.photo_count}.jpg"
            cv2.imwrite(photo_name, self.frame)
            print(f"Photo saved: {photo_name}")

            # Show the captured photo in a new window
            captured_image = cv2.imread(photo_name)
            if captured_image is not None:
                cv2.imshow("Captured Photo", captured_image)
                self.display_price_window()  # Show the price window after capturing the photo
            else:
                print("Error: Could not load the captured photo.")
            self.photo_count += 1

    def retry_action(self):
        # Close both the price window and the captured photo window
        if hasattr(self, 'tk_window') and self.tk_window.winfo_exists():
            self.tk_window.destroy()
        if cv2.getWindowProperty("Captured Photo", cv2.WND_PROP_VISIBLE) >= 1:
            cv2.destroyWindow("Captured Photo")
        self.show_price_window = False  # Reset flag

    def quit_action(self):
        self.running = False  # Stop the camera feed
        if hasattr(self, 'tk_window') and self.tk_window.winfo_exists():
            self.tk_window.destroy()
        if cv2.getWindowProperty("Captured Photo", cv2.WND_PROP_VISIBLE) >= 1:
            cv2.destroyWindow("Captured Photo")
        cv2.destroyAllWindows()  # Close all OpenCV windows

    # Close only the cashier checkout window
    def close_cashier_checkout(self):
        if hasattr(self, 'tk_window') and self.tk_window.winfo_exists():
            self.tk_window.destroy()

    def display_price_window(self):
        self.tk_window = tk.Tk()
        self.tk_window.title("Cashier Checkout")
        self.tk_window.attributes("-fullscreen", True)
        self.tk_window.configure(bg="#F8F9FA")  # Light gray background

        title_label = tk.Label(self.tk_window, text="Cashier Checkout", font=("Helvetica", 32, "bold"), bg="#F8F9FA", fg="#333333")
        title_label.pack(pady=20)

        frame = tk.Frame(self.tk_window, bg="#FFFFFF", bd=2, relief="raised")  # Changed to raised for a cleaner look
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Add a separator line
        separator = ttk.Separator(self.tk_window, orient="horizontal")
        separator.pack(fill="x", padx=20)

        # Create a list of detected items
        for item_name, data in self.detected_objects.items():
            price = self.prices.get(item_name.lower(), 10)
            count = data['count']
            total_for_item = data['total']
            item_text = f"{item_name.capitalize()} (Price: ${price} | Qty: {count} | Total: ${total_for_item})"
            item_label = tk.Label(frame, text=item_text, font=("Helvetica", 18), anchor="w", bg="#FFFFFF", fg="#555555")
            item_label.pack(fill="x", padx=25, pady=5)  # More refined padding

        # Total price display
        total_price_text = f"Total Price: ${self.total_price}"
        total_price_label = tk.Label(frame, text=total_price_text, font=("Helvetica", 24, "bold"), bg="#FFFFFF", fg="#D9534F")
        total_price_label.pack(pady=20)

        # Button frame with improved styling
        button_frame = tk.Frame(self.tk_window, bg="#F8F9FA")
        button_frame.pack(pady=20)

        retry_button = ttk.Button(button_frame, text="Retry", command=self.retry_action, style="Accent.TButton")
        retry_button.grid(row=0, column=0, padx=20, pady=10)

        # Updated quit button to only close the cashier checkout window
        quit_button = ttk.Button(button_frame, text="Quit", command=self.close_cashier_checkout, style="Accent.TButton")
        quit_button.grid(row=0, column=1, padx=20, pady=10)

        # Apply style to buttons
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Helvetica", 14, "bold"), padding=10)
        style.map("Accent.TButton", foreground=[('active', '#FFFFFF')], background=[('active', '#D9534F')])  # Change button color on hover

        self.tk_window.mainloop()


# Initialize and run the camera object
cam = MobileCamera()
cam.getVideo("http://192.168.1.138:8080/video")
