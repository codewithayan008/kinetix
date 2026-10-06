from flask import Flask, render_template, request, Response, jsonify
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os

app = Flask(__name__)

base_options = python.BaseOptions(model_asset_path='pose_landmarker_heavy.task')
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    min_pose_detection_confidence=0.5,
    min_pose_presence_confidence=0.5,
    min_tracking_confidence=0.5
)
detector = vision.PoseLandmarker.create_from_options(options)

latest_analysis = "Waiting to start analysis..."

POSE_CONNECTIONS = [(0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8), (9, 10), 
                    (11, 12), (11, 13), (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
                    (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20), (11, 23), 
                    (12, 24), (23, 24), (23, 25), (24, 26), (25, 27), (26, 28), (27, 29), 
                    (28, 30), (29, 31), (30, 32), (27, 31), (28, 32)]

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return int(angle)

def generate_frames():
    global latest_analysis
    cap = cv2.VideoCapture(0)
    timestamp_ms = 0
    
    while True:
        success, frame = cap.read()
        if not success:
            break
            
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        timestamp_ms += 33
        
        detection_result = detector.detect_for_video(mp_image, timestamp_ms)
        
        analysis_parts = []
        
        if detection_result.pose_landmarks:
            landmarks = detection_result.pose_landmarks[0]
            h, w, _ = frame.shape
            
            # Helper to check if a landmark has high enough visibility confidence
            def is_visible(idx, threshold=0.5):
                return landmarks[idx].visibility > threshold if hasattr(landmarks[idx], 'visibility') else True

            def get_coords(index):
                return [landmarks[index].x, landmarks[index].y]

            try:
                # --- HEAD ---
                if is_visible(0) and is_visible(7) and is_visible(8):
                    nose = landmarks[0]
                    left_ear = landmarks[7]
                    right_ear = landmarks[8]
                    ear_mid_x = (left_ear.x + right_ear.x) / 2.0
                    ear_dist = abs(left_ear.x - right_ear.x)
                    
                    if ear_dist > 0:
                        turn_ratio = (nose.x - ear_mid_x) / (ear_dist / 2.0)
                        turn_ratio = max(-1.0, min(1.0, turn_ratio))
                        head_angle = int(turn_ratio * 90)
                        if head_angle > 15:
                            analysis_parts.append(f"Head: Left {abs(head_angle)}°")
                        elif head_angle < -15:
                            analysis_parts.append(f"Head: Right {abs(head_angle)}°")
                        else:
                            analysis_parts.append("Head: Straight")

                # --- RIGHT ELBOW --- (Indices 12, 14, 16)
                if is_visible(12) and is_visible(14) and is_visible(16):
                    angle = calculate_angle(get_coords(12), get_coords(14), get_coords(16))
                    analysis_parts.append(f"Right Elbow: {angle}°")

                # --- LEFT ELBOW --- (Indices 11, 13, 15)
                if is_visible(11) and is_visible(13) and is_visible(15):
                    angle = calculate_angle(get_coords(11), get_coords(13), get_coords(15))
                    analysis_parts.append(f"Left Elbow: {angle}°")

                # --- RIGHT KNEE --- (Indices 24, 26, 28)
                if is_visible(24) and is_visible(26) and is_visible(28):
                    angle = calculate_angle(get_coords(24), get_coords(26), get_coords(28))
                    analysis_parts.append(f"Right Knee: {angle}°")

                # --- LEFT KNEE --- (Indices 23, 25, 27)
                if is_visible(23) and is_visible(25) and is_visible(27):
                    angle = calculate_angle(get_coords(23), get_coords(25), get_coords(27))
                    analysis_parts.append(f"Left Knee: {angle}°")

                if analysis_parts:
                    latest_analysis = " | ".join(analysis_parts)
                else:
                    latest_analysis = "Position yourself clearly in front of the camera."

            except Exception:
                pass
            
            # Draw outlines
            for connection in POSE_CONNECTIONS:
                start_idx, end_idx = connection
                if start_idx < len(landmarks) and end_idx < len(landmarks):
                    start_pt = (int(landmarks[start_idx].x * w), int(landmarks[start_idx].y * h))
                    end_pt = (int(landmarks[end_idx].x * w), int(landmarks[end_idx].y * h))
                    cv2.line(frame, start_pt, end_pt, (245, 66, 230), 2)
            
            for lm in landmarks:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 3, (245, 117, 66), -1)
        else:
            latest_analysis = "No body detected."
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        name = request.form.get('name')
        return render_template('tracker.html', name=name)
    return render_template('setup.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_analysis')
def get_analysis():
    return jsonify({"analysis": latest_analysis})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)