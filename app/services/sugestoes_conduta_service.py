from app.infra.ai_client import gerar_texto
import re


def anonimizar_texto(texto: str) -> str:
    if not texto:
        return texto

    texto = re.sub(r"\d{2}/\d{2}/\d{4}", "[DATA]", texto)
    texto = re.sub(r"\d{2}/\d{2}", "[DATA]", texto)
    texto = re.sub(r"\b\d{1,3}\s?anos\b", "idade não informada", texto, flags=re.IGNORECASE)

    return texto


def normalizar_lista_numerada(texto: str) -> str:
    if not texto:
        return ""

    texto = texto.strip()

    # garante quebra de linha antes de cada item numerado
    texto = re.sub(r"\s*(\d+\.\s)", r"\n\1", texto)

    # remove linha em branco inicial, se surgir
    texto = texto.lstrip()

    # reduz excesso de linhas
    texto = re.sub(r"\n{2,}", "\n", texto)

    return texto.strip()


def sugerir_condutas(texto_caso: str) -> str:
    texto_caso = anonimizar_texto(texto_caso)

    prompt = f"""
Você é um médico emergencista experiente.

Sua função é analisar um caso clínico já estruturado e sugerir condutas adicionais relevantes.

Regras obrigatórias:
- NÃO reescrever o caso.
- NÃO repetir condutas já descritas.
- NÃO inventar dados ausentes.
- NÃO usar markdown ou asteriscos.
- NÃO explicar fora da lista.
- Cada item da lista deve ficar em uma linha separada.

Raciocínio clínico esperado:
- Priorizar risco de morte e instabilidade.
- Identificar lacunas na condução.
- Sugerir condutas práticas e acionáveis.
- Considerar necessidade de monitorização, exames, suporte e especialidades.
- Quando houver incerteza por falta de dados, explicitar brevemente.

Formato obrigatório:

1. ...
2. ...
3. ...

Caso clínico:
{texto_caso}
"""

    sugestoes = gerar_texto(prompt)
    sugestoes = normalizar_lista_numerada(sugestoes)

    if not sugestoes.strip():
        return ""

    return f"»» Sugestões de conduta:\n{sugestoes}"