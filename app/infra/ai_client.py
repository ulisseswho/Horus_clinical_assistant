import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def get_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY não encontrada")

    return OpenAI(api_key=api_key)


def gerar_texto(prompt: str) -> str:
    client = get_client()

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text if response.output_text else ""