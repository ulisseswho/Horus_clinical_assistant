import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY não encontrada")

    return OpenAI(api_key=api_key)


def gerar_texto(prompt: str, modelo: str = "gpt-4.1-mini") -> str:
    client = get_client()

    try:
        response = client.responses.create(
            model=modelo,
            input=prompt
        )

        # Forma simples (quando disponível)
        if hasattr(response, "output_text") and response.output_text:
            return response.output_text

        # Fallback seguro
        texto = ""
        for item in response.output:
            if item.type == "output_text":
                texto += item.text

        return texto.strip()

    except Exception as e:
        print(f"Erro na IA: {e}")
        return ""