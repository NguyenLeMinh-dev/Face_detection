from flask import Flask, render_template, Response, request
import cv2
import mediapipe as mp

app = Flask(__name__)
face_detection_on = True

# MediaPipe setup
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

# Video capture
cap = cv2.VideoCapture(0)

def gen_frames():
    global face_detection_on
    while True:
        success, frame = cap.read()
        if not success:
            break

        if face_detection_on:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detection.process(frame_rgb)
            if results.detections:
                for detection in results.detections:
                    mp_drawing.draw_detection(frame, detection)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/toggle', methods=['POST'])
def toggle_detection():
    global face_detection_on
    face_detection_on = not face_detection_on
    return ('', 204)

if __name__ == '__main__':
    app.run(debug=True)
