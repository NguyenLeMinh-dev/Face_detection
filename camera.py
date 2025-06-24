import cv2
import threading
import numpy as np
import mediapipe as mp

class VideoCamera:
    def __init__(self, src=0, scale=0.75):
        self.cap = cv2.VideoCapture(src)
        self.scale = scale
        self.running = True
        self.frame = None

        # MediaPipe Face Detection
        mp_fd = mp.solutions.face_detection
        self.detector = mp_fd.FaceDetection(model_selection=0, min_detection_confidence=0.5)
        self.drawing = mp.solutions.drawing_utils

        # Thread đọc frame liên tục
        thread = threading.Thread(target=self._update_frames, daemon=True)
        thread.start()

    def _update_frames(self):
        while self.running:
            success, frame = self.cap.read()
            if not success:
                continue
            # resize để tăng tốc xử lý
            h, w = frame.shape[:2]
            frame = cv2.resize(frame, (int(w*self.scale), int(h*self.scale)))
            self.frame = frame

    def get_frame(self, detect=True):
        """
        Trả về (jpeg_bytes, face_count).
        Nếu detect=True sẽ vẽ bounding boxes và đếm số face.
        """
        if self.frame is None:
            return None, 0

        frame = self.frame.copy()
        count = 0
        if detect:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.detector.process(rgb)
            if results.detections:
                count = len(results.detections)
                for det in results.detections:
                    self.drawing.draw_detection(frame, det)

        ret, buf = cv2.imencode('.jpg', frame)
        return buf.tobytes(), count

    def release(self):
        self.running = False
        self.cap.release()
