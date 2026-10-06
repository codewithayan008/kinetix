FROM python:3.11-slim

# Install all necessary OpenGL, EGL, and C++ system libraries for MediaPipe
RUN apt-get update && apt-get install -y \
    libgles2 \
    libgl1 \
    libglib2.0-0 \
    libegl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your project files
COPY . .

# Start the server using Render's dynamic port
CMD gunicorn app:app --bind 0.0.0.0:$PORT