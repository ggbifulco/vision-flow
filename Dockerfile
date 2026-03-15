FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# System dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p outputs/screenshots

EXPOSE 8000

CMD ["python", "main.py", "--mode", "web"]
