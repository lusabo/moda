import cv2
import base64
import time
import logging

def capture_frame_from_webcam():
    video = cv2.VideoCapture(0)
    base64_frame = None
    captured_frame = False
    time.sleep(2)
    while video.isOpened():
        success, frame = video.read()
        if not success:
            logging.error("Falha ao ler frame da webcam.")
            break
        if not captured_frame:
            _, buffer = cv2.imencode(".jpg", frame)
            base64_frame = base64.b64encode(buffer).decode("utf-8")
            captured_frame = True
        cv2.imshow('Webcam Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    video.release()
    cv2.destroyAllWindows()
    if captured_frame:
        logging.info("Frame capturado para análise.")
    else:
        logging.error("Nenhum frame foi capturado.")
    return base64_frame