import os
import requests
import tempfile
import logging
from openai import OpenAI

# Carregar chave da API do OpenAI de variável de ambiente
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    logging.error("OPENAI_API_KEY não está definida nas variáveis de ambiente.")
    raise ValueError("OPENAI_API_KEY não está definida nas variáveis de ambiente.")

client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_frame(base64_frame):
    prompt_messages = [
        {
            "role": "user",
            "content": """
            Estes são frames de um vídeo que desejo enviar. 
            Gostaria de analisar se a pessoa capturada no vídeo está na moda. Por favor, observe o vídeo e avalie a aparência da pessoa com base nos seguintes critérios:
            1. Roupas e Estilo: As roupas que a pessoa está usando são consideradas modernas e em linha com as tendências atuais da moda? Mencione marcas, cortes, cores, padrões e acessórios que estão na moda.
            2. Combinação de Cores: As combinações de cores usadas estão em harmonia e seguem as tendências de cores atuais?
            3. Acessórios: A pessoa está usando acessórios que estão em alta, como jóias, bolsas, chapéus, óculos, etc.?
            4. Calçados: Os calçados usados são populares e considerados estilosos no momento?
            5. Cabelo e Maquiagem: O estilo de cabelo e maquiagem está em linha com as tendências atuais? Considere cortes de cabelo, cores, penteados, e técnicas de maquiagem.
            6. Ajuste e Proporções: As roupas e acessórios têm um bom ajuste e proporções que seguem as recomendações de estilo atuais?
            7. Inspirações de Moda: A aparência da pessoa se inspira claramente em influenciadores de moda, celebridades ou desfiles de moda recentes?
            8. Contexto: O estilo da pessoa é apropriado para a ocasião ou evento capturado no vídeo?
            Baseado nesses critérios, forneça uma avaliação detalhada e uma nota final sobre se a pessoa está na moda ou não.
            """,
            {"image": base64_frame, "resize": 768},
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
            "content": f"""
            Este é um frame de um vídeo. 
            Crie uma pequena narração no estilo de Clodovil Hernandes sobre a aparência
            da pessoa analisada conforme a seguinte descrição:
            {description}
            Inclua apenas a narração.
            """,
            {"image": base64_frame, "resize": 768},
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
