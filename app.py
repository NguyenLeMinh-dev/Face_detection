from flask import Flask, render_template, Response, request, jsonify, send_from_directory
import numpy as np
import cv2
import os
import datetime
from camera import VideoCamera

app = Flask(__name__)

# Khởi camera với scale (resize) 50%
cam = VideoCamera(scale=0.5)

# Trạng thái global
face_on = True
recording = False
video_writer = None

# Thư mục lưu ảnh/video
OUTPUT_DIR = 'static/snapshots'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def gen():
    global recording, video_writer
    while True:
        frame_bytes, face_count = cam.get_frame(detect=face_on)
        if frame_bytes is None:
            continue

        # Ghi video nếu cần
        if recording:
            if video_writer is None:
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                h, w = cam.frame.shape[:2]
                video_writer = cv2.VideoWriter(f'{OUTPUT_DIR}/record_{now}.avi', fourcc, 20.0, (w, h))
            frame_bgr = cv2.imdecode(np.frombuffer(frame_bytes, np.uint8), cv2.IMREAD_COLOR)
            video_writer.write(frame_bgr)

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/toggle_face', methods=['POST'])
def toggle_face():
    global face_on
    face_on = not face_on
    return jsonify({'face_on': face_on})

@app.route('/snapshot', methods=['POST'])
def snapshot():
    data, _ = cam.get_frame(detect=False)
    if data:
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'snap_{now}.jpg'
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, 'wb') as f:
            f.write(data)
        return jsonify({'saved': True, 'path': f'/static/snapshots/{filename}'})
    return jsonify({'saved': False}), 500

@app.route('/toggle_record', methods=['POST'])
def toggle_record():
    global recording, video_writer
    recording = not recording
    if not recording and video_writer:
        video_writer.release()
        video_writer = None
    return jsonify({'recording': recording})

@app.route('/face_count')
def face_count():
    _, count = cam.get_frame(detect=face_on)
    return jsonify({'count': count})

if __name__ == '__main__':
    app.run(debug=True)
