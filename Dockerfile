FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Prevent ultralytics from opening GUI
    MPLBACKEND=Agg

# System dependencies
# libgl1 + libglib2.0-0 → OpenCV headless
# libglib2.0-0 libsm6 libxrender1 libxext6 → some cv2 backends
# ffmpeg → RTSP / video file support
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
# Replace opencv-python with headless variant (no X11/GUI needed in server mode)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --force-reinstall opencv-python-headless

# Copy source
COPY . .

# Create output directories
RUN mkdir -p outputs/screenshots

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["python", "main.py", "--mode", "web"]
