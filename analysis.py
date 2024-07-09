import os
import requests
import tempfile
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Carregar chave da API do OpenAI de variável de ambiente
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    logging.error("OPENAI_API_KEY não está definida nas variáveis de ambiente.")
    raise ValueError("OPENAI_API_KEY não está definida nas variáveis de ambiente.")

client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_frame(base64_frame):
    prompt_messages = [
        {
            "role": "user",
            "content": [
                """
                Estes é o frame de um vídeo que desejo enviar. 
                Gostaria de avaliar se a pessoa no vídeo está na moda, considerando os seguintes critérios: 
                roupas e estilo (modernidade, tendências, marcas, cortes, cores, padrões e acessórios); 
                combinação de cores (harmonia e tendências atuais); uso de acessórios populares (jóias, 
                bolsas, chapéus, óculos, etc.); calçados (popularidade e estilo); cabelo e maquiagem 
                (tendências em cortes, cores, penteados e técnicas de maquiagem); ajuste e proporções 
                (conformidade com recomendações de estilo); inspirações de moda (influência de moda recente, 
                celebridades ou desfiles); e contexto (adequação para a ocasião do vídeo). Baseado nesses 
                critérios, forneça uma avaliação detalhada e uma nota final sobre se a pessoa está na moda 
                ou não.
                """,
                {"image": base64_frame, "resize": 768},
            ]
        },
    ]
    params = {
        "model": "gpt-4o",
        "messages": prompt_messages,
        "max_tokens": 200,
    }
    result = client.chat.completions.create(**params)
    description = result.choices[0].message.content.strip()
    logging.info("Análise do frame concluída.")
    return description

def create_narration(description, base64_frame):
    prompt_messages = [
        {
            "role": "user",
            "content": [
                f"""
                Este é um frame de um vídeo. 
                Crie uma frase sobre a aparência da pessoa analisada conforme a descrição:
                {description}
                Inclua apenas a narração.
                """,
                {"image": base64_frame, "resize": 768},
            ]
        },
    ]
    params = {
        "model": "gpt-4o",
        "messages": prompt_messages,
        "max_tokens": 300,
    }
    result = client.chat.completions.create(**params)
    narration_script = result.choices[0].message.content.strip()
    logging.info("Narração criada.")
    return narration_script

def generate_audio(narration_script):
    response = requests.post(
        "https://api.openai.com/v1/audio/speech",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        },
        json={
            "model": "tts-1-1106",
            "input": narration_script,
            "voice": "onyx",
        },
    )
    audio = b""
    for chunk in response.iter_content(chunk_size=1024 * 1024):
        audio += chunk
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio_file:
        temp_audio_file.write(audio)
        temp_audio_path = temp_audio_file.name
    logging.info("Áudio gerado.")
    return temp_audio_path
