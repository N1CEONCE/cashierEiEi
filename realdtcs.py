import cv2
import threading
from collections import defaultdict
from ultralytics import YOLO
import tkinter as tk
from PIL import Image, ImageTk


class MobileCamera:
    def __init__(self, camera_url, app):
        self.model = YOLO('yolov8n.pt')  # Use 'yolov8n.pt' or any desired model
        self.frame = None
        self.running = True
        self.frame_skip = 0
        self.detected_objects = defaultdict(lambda: {'count': 0, 'total': 0})
        self.prices = {
            "apple": 1,
            "banana": 2,
            "orange": 3,
            "bottle": 4,
            "mouse": 5,
        }
        self.app = app
        self.getVideo(camera_url)

    def getVideo(self, camera):
        self.camera = camera
        cap = cv2.VideoCapture(self.camera)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        def capture_frames():
            while self.running:
                ret, frame = cap.read()
                if ret:
                    self.frame = frame

        thread = threading.Thread(target=capture_frames)
        thread.start()

        while self.running:
            if self.frame is not None:
                if self.frame_skip % 2 == 0:
                    results = self.model(self.frame)
                    self.detected_objects.clear()

                    for result in results:
                        boxes = result.boxes
                        for box in boxes:
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            conf = box.conf[0]
                            cls = int(box.cls[0])

                            if conf > 0.5:
                                cv2.rectangle(self.frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                                class_name = self.model.names[cls]
                                price_tag = self.prices.get(class_name.lower(), 0)

                                if class_name.lower() in self.prices:
                                    self.detected_objects[class_name]['count'] += 1
                                    self.detected_objects[class_name]['total'] = self.detected_objects[class_name][
                                                                                     'count'] * price_tag

                                cv2.putText(self.frame, f"{class_name}: ${price_tag}",
                                            (x1, y1 - 10),
                                            cv2.FONT_HERSHEY_SIMPLEX,
                                            1,
                                            (0, 255, 0),
                                            2)

                    self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(self.frame)
                    img.thumbnail((960, 720), Image.Resampling.LANCZOS)
                    imgtk = ImageTk.PhotoImage(image=img)

                    self.app.video_label.imgtk = imgtk
                    self.app.video_label.config(image=imgtk)

                self.frame_skip += 1

            self.app.root.update_idletasks()
            self.app.root.update()

        cap.release()
        thread.join()
        cv2.destroyAllWindows()




class App:
    def __init__(self, root, camera_url):
        self.root = root
        self.root.title("Mobile Camera with Object Detection")
        self.root.geometry("1440x800")  # Larger window size

        # Video display label
        self.video_label = tk.Label(self.root)
        self.video_label.grid(row=0, column=0, rowspan=5, padx=10, pady=10, sticky="n")

        # Buttons frame on the right side
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        # Large button styling
        button_style = {"padx": 20, "pady": 20, "font": ("Arial", 20)}

        # Scan button
        self.scan_button = tk.Button(button_frame, text="Scan", command=self.scan, **button_style)
        self.scan_button.pack(pady=10)

        # Retry button
        self.retry_button = tk.Button(button_frame, text="Retry", command=self.retry, **button_style)
        self.retry_button.pack(pady=10)

        # Quit button
        self.quit_button = tk.Button(button_frame, text="Quit", command=self.quit, **button_style)
        self.quit_button.pack(pady=10)

        # Start the camera
        self.camera = MobileCamera(camera_url, self)

    def scan(self):
        # Implement scan functionality here
        print("Scan button pressed")

    def retry(self):
        # Implement retry functionality here
        print("Retry button pressed")

    def quit(self):
        # Implement quit functionality
        self.camera.running = False
        self.root.quit()


# Main Tkinter window setup
root = tk.Tk()
app = App(root, "http://192.168.1.164:8080/video")  # Replace with your mobile camera URL
root.mainloop()
