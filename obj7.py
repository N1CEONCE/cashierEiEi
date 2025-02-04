import cv2
import threading
import numpy as np
from collections import defaultdict
from ultralytics import YOLO


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
        if cv2.getWindowProperty("Price & Name Display", cv2.WND_PROP_VISIBLE) >= 1:
            cv2.destroyWindow("Price & Name Display")
        if cv2.getWindowProperty("Captured Photo", cv2.WND_PROP_VISIBLE) >= 1:
            cv2.destroyWindow("Captured Photo")
        self.show_price_window = False  # Reset flag

    def quit_action(self):
        self.running = False  # Stop the camera feed
        if cv2.getWindowProperty("Price & Name Display", cv2.WND_PROP_VISIBLE) >= 1:
            cv2.destroyWindow("Price & Name Display")
        if cv2.getWindowProperty("Captured Photo", cv2.WND_PROP_VISIBLE) >= 1:
            cv2.destroyWindow("Captured Photo")
        cv2.destroyAllWindows()  # Close all OpenCV windows

    def display_price_window(self):
        # Create a full-screen white window to display the item prices and total price
        screen_res = (1080, 1920)  # Use screen resolution or a large window size
        white_image = np.ones(screen_res + (3,), dtype=np.uint8) * 255  # Full-screen white background

        # Font for displaying text on the white window
        font = cv2.FONT_HERSHEY_COMPLEX

        y_offset = 100  # Starting y position for the first item
        line_spacing = 40  # Line spacing between items

        # Header text for the checkout window
        header_text = "Cashier Checkout"
        cv2.putText(white_image, header_text, (100, y_offset), font, 1.2, (0, 0, 0), 2)

        y_offset += line_spacing * 2  # Move down for the first item

        # Display each detected object, its price, quantity, and total price
        for item_name, data in self.detected_objects.items():
            price = self.prices.get(item_name.lower(), 10)
            count = data['count']
            total_for_item = data['total']
            item_text = f"Item: {item_name} Price: ${price} Amount: {count} Total: ${price} x {count} = ${total_for_item}"
            cv2.putText(white_image, item_text, (100, y_offset), font, 1, (0, 0, 0), 2)
            y_offset += line_spacing

        # Display cumulative total price at the end
        total_price_text = f"Total Price: ${self.total_price}"
        cv2.putText(white_image, total_price_text, (100, y_offset + line_spacing), font, 1, (0, 0, 0), 2)

        # Draw "Retry" button on the white window
        cv2.rectangle(white_image, (100, y_offset + line_spacing * 3), (300, y_offset + line_spacing * 4),
                      (200, 200, 200), -1)
        cv2.putText(white_image, "Retry", (130, y_offset + line_spacing * 4 - 15), font, 1, (0, 0, 0), 2)

        # Set the mouse callback to detect click on the Retry button
        cv2.imshow("Price & Name Display", white_image)
        cv2.setMouseCallback("Price & Name Display", self.price_window_callback)

    def price_window_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # Check if "Retry" button on the price window was clicked
            if 100 < x < 300 and 300 < y < 350:
                self.retry_action()


# Create an instance of MobileCamera
cam = MobileCamera()
cam.getVideo("http://192.168.1.113:8080/video")
