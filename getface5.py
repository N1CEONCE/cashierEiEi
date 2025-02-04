import cv2
import threading
import numpy as np

class MobileCamera:
    def __init__(self):
        # Load the pre-trained Haar Cascade classifier for face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.frame = None
        self.running = True
        self.frame_skip = 0  # Initialize frame skip
        self.photo_count = 0  # To count the saved photos
        self.price = 10  # Example price for each detected face (numerical value)
        self.total_price = 0  # To accumulate the total price
        self.detected_faces = 0  # To track the number of detected faces
        self.name = "Human"  # Example item name for display

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
                    # Convert the frame to grayscale for face detection
                    gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

                    # Detect faces
                    faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                    # If faces are detected, add the price for each face
                    if len(faces) > 0:
                        self.detected_faces = len(faces)
                        self.total_price = self.detected_faces * self.price  # Calculate total price based on detected faces

                    # Draw rectangles around detected faces
                    for (x, y, w, h) in faces:
                        # Draw rectangle around the face
                        cv2.rectangle(self.frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                        # Display price tag for each face
                        cv2.putText(self.frame, f"Price: ${self.price}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    # Display the frame with face detection
                    cv2.imshow("Mobile Cam - Face Detection", self.frame)

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
                amount_text = f"Price: ${self.price} x {self.detected_faces} (amount of objects)"
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
cam.getVideo("http://192.168.1.192:8080/video")
