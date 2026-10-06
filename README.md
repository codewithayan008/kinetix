# 🚀 Kinetix - Advanced Human Pose Analysis

Kinetix is a real-time computer vision and pose tracking web application built with **Flask**, **MediaPipe**, **OpenCV**, and **WebSockets**. It tracks human body joints, calculates joint angles (elbows, knees, and head orientation), and renders a live skeletal overlay directly in the user's browser.

---

## 🌐 Live Demos & Access Links

*   **Production Deployment (Render):** [https://kinetix-2.onrender.com/](https://kinetix-2.onrender.com/)
*   **Active Dev Tunnel (Localhost):** [https://18fl30m8-5000.inc1.devtunnels.ms/](https://18fl30m8-5000.inc1.devtunnels.ms/)

---

## ✨ Key Features

*   **Real-Time Pose Estimation:** Powered by MediaPipe's robust `PoseLandmarker` machine learning model (`pose_landmarker_heavy.task`).
*   **Client-Server WebSocket Architecture:** Bypasses cloud server hardware restrictions by streaming local browser camera frames via WebSockets (`Flask-SocketIO`) to process AI analytics in Python.
*   **Angle Calculations & Form Analysis:** Automatically computes precise angles for elbows and knees, alongside head orientation tracking.
*   **Cloud Optimized:** Fully configured to run seamlessly on containerized hosting services like Render using Gunicorn and standard threading (`gthread`).

---

## 🛠️ Tech Stack

*   **Backend:** Python, Flask, Flask-SocketIO, OpenCV (`opencv-python-headless`), NumPy, MediaPipe
*   **Frontend:** HTML5, CSS3, JavaScript (WebSockets, MediaDevices API, Canvas API)
*   **Hosting/Deployment:** Render, Docker, Gunicorn

---

## ⚙️ Local Installation & Running Guide

If you want to run this project locally on your machine, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/kinetix.git](https://github.com/your-username/kinetix.git)
   cd kinetix
