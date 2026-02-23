import cv2
from src.core.engine import VisionFlowEngine
from src.config.settings import Settings

def run_vision_flow():
    print("🚀 VisionFlow: Inizializzazione Multimodal Engine...")
    engine = VisionFlowEngine()
    
    # 0 = Webcam locale. Puoi sostituire con un link RTSP o un path di un video.mp4
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("[Error] Impossibile accedere alla webcam.")
        return

    print("[√] Stream avviato. Premi 'q' per uscire.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Ridimensioniamo per performance consistenti
        frame = cv2.resize(frame, (Settings.DISPLAY_WIDTH, Settings.DISPLAY_HEIGHT))

        # Elaborazione frame tramite l'orchestratore
        processed_frame, analysis_text = engine.process_frame(frame)

        # Mostra il risultato in tempo reale
        cv2.imshow("BGG VisionFlow - YOLOv11 + Moondream2", processed_frame)

        # Log dell'analisi in console se aggiornata
        if engine.frame_count % 150 == 0:
            print(f"
[AI Analysis]: {analysis_text}")

        # Tasto Q per uscire
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[*] VisionFlow terminato correttamente.")

if __name__ == "__main__":
    run_vision_flow()
