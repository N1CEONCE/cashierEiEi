import cv2
import threading
import numpy as np
from ultralytics import YOLO

class MobileCamera:
    def __init__(self):
        # Load YOLOv8 model for object detection
        self.model = YOLO('yolov8n.pt')  # Use 'yolov8n.pt' or any desired model
        self.frame = None
        self.running = True
        self.frame_skip = 0  # Initialize frame skip
        self.photo_count = 0  # To count the saved photos
        self.price = 10  # Example price for each detected object
        self.total_price = 0  # To accumulate the total price
        self.detected_objects = 0  # To track the number of detected objects
        self.name = "Object"  # Example item name for display

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

        while True:
            if self.frame is not None:
                # Skip every 2nd frame to reduce processing load
                if self.frame_skip % 2 == 0:
                    # Detect objects using YOLOv8 model
                    results = self.model(self.frame)

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

                                # Display class name and price tag
                                price_tag = self.price  # Use defined price
                                cv2.putText(self.frame, f"{class_name}: ${price_tag}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    # If objects are detected, add the price for each object
                    self.detected_objects = len(boxes)
                    self.total_price = self.detected_objects * self.price  # Calculate total price based on detected objects

                    # Display the frame with object detection
                    cv2.imshow("Mobile Cam - Object Detection", self.frame)

                self.frame_skip += 1

            # Capture the photo when 'c' is pressed
            key = cv2.waitKey(1)
            if key == ord('c') and self.frame is not None:
                # Save the current frame as an image
                photo_name = f"detected_photo_{self.photo_count}.jpg"
                cv2.imwrite(photo_name, self.frame)
                print(f"Photo saved: {photo_name}")

                # Show the captured photo in a new window
                captured_image = cv2.imread(photo_name)
                if captured_image is not None:
                    cv2.imshow("Captured Photo", captured_image)
                else:
                    print("Error: Could not load the captured photo.")

                # Create a new big white window to display the price, total price, amount, and name
                white_image = np.ones((600, 800, 3), dtype=np.uint8) * 255  # White background
                amount_text = f"Price: ${self.price} x {self.detected_objects} (amount of objects)"
                total_text = f"Total: ${self.total_price}"
                cv2.putText(white_image, f"Name: {self.name}", (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 5)
                cv2.putText(white_image, amount_text, (100, 250), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 5)
                cv2.putText(white_image, total_text, (100, 350), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 5)
                cv2.imshow("Price & Name Display", white_image)

                self.photo_count += 1

            # Exit the loop when 'q' is pressed
            if key == ord('q'):
                self.running = False
                break

        cap.release()
        thread.join()
        cv2.destroyAllWindows()

# Create an instance of MobileCamera
cam = MobileCamera()
cam.getVideo("http://192.168.61.178:8080/video")
