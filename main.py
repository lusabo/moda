import os
import logging
from analysis import analyze_frame, create_narration, generate_audio
from webcam import capture_frame_from_webcam
from playsound import playsound
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def play_audio(file_path):
    playsound(file_path)
    logging.info("Narração reproduzida.")

def main():
    try:
        base64_frame = capture_frame_from_webcam()
        if base64_frame:
            description = analyze_frame(base64_frame)
            narration_script = create_narration(description, base64_frame)
            temp_audio_path = generate_audio(narration_script)
            play_audio(temp_audio_path)
    except Exception as e:
        logging.error(f"Erro durante a execução: {e}")

if __name__ == "__main__":
    main()
