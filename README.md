# VisionFlow: Real-time Multimodal Intelligent Monitoring

[![YOLOv11](https://img.shields.io/badge/Model-YOLOv11-red.svg)](https://ultralytics.com/)
[![Moondream2](https://img.shields.io/badge/VLM-Moondream2-blue.svg)](https://huggingface.co/vikhyatk/moondream2)
[![FastAPI](https://img.shields.io/badge/Interface-FastAPI-green.svg)](https://fastapi.tiangolo.com/)

## 👁️ Project Overview
VisionFlow is an advanced multimodal surveillance and analysis engine. It bridges the gap between traditional object detection and high-level semantic understanding. The system doesn't just "see" objects; it "understands" actions and context using an integrated Vision-Language Model (VLM).

## 🧠 Key Features
-   **Dual-Engine Inference**: High-speed object tracking with **YOLOv11** combined with deep semantic analysis via **Moondream2**.
-   **Asynchronous Processing**: Optimized pipeline to maintain smooth video frame rates while performing heavy VLM reasoning.
-   **Edge-Ready Architecture**: Designed for low-latency performance on consumer hardware and Edge devices.
-   **Interactive QA**: (Upcoming) Query the video stream in natural language.

## 🛠️ Tech Stack
-   **Detection & Tracking**: Ultralytics YOLOv11
-   **Visual Reasoning**: Moondream2 (Transformers)
-   **Frameworks**: PyTorch, OpenCV
-   **Language**: Python 3.10+

## 📦 Installation & Setup
1.  **Clone & Install**:
    ```bash
    git clone https://github.com/ggbifulco/vision-flow.git
    cd vision-flow
    pip install -r requirements.txt
    ```
2.  **Run with Webcam**:
    ```bash
    python main.py
    ```

---
**Author**: [Giuseppe Gerardo Bifulco](https://tuo-portfolio.vercel.app)
