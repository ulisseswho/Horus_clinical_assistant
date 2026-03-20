from app.services.atendimento_service import organizar_atendimento
from app.services.sanitizacao_service import sanitizar_texto
from app.services.pos_processamento import aplicar_regras
import re


def limpar_saida(texto: str) -> str:
    if not texto:
        return texto

    # 1. Garantir parâmetros sempre vazios
    texto = re.sub(
        r"»» Parâmetros na admissão:\s*.*?(?=\n»» |\Z)",
        "»» Parâmetros na admissão:\nPA - mmHg || FC - bpm || FR - irpm || Temp - °C || SatO2 - % || Glicemia - mg/dL",
        texto,
        flags=re.DOTALL,
    )

    # 2. Remover hífen no início de QP e HDA
    texto = re.sub(r"(»» Queixa Principal:\s*)-\s*", r"\1", texto)
    texto = re.sub(r"(»» História da Doença Atual:\s*)-\s*", r"\1", texto)

    # 3. Padronizar seções
    texto = re.sub(r"\n*»» ", r"\n\n»» ", texto)

    # 4. Remover excesso de linhas
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    return texto.strip()

    # 5. Normalizar lista numerada em Condutas
    match_condutas = re.search(r"(»» Condutas:\n)(.*)", texto, re.DOTALL)
    if match_condutas:
        cabecalho = match_condutas.group(1)
        conteudo = match_condutas.group(2).strip()

        # remove linhas em branco extras dentro da lista
        conteudo = re.sub(r"\n{2,}", "\n", conteudo)

        # garante cada item numerado em sua própria linha
        conteudo = re.sub(r"\s*(\d+\.\s)", r"\n\1", conteudo)
        conteudo = conteudo.lstrip()
        conteudo = re.sub(r"\n{2,}", "\n", conteudo)

        texto = re.sub(
            r"»» Condutas:\n.*",
            f"{cabecalho}{conteudo}",
            texto,
            flags=re.DOTALL
        )

def processar_texto_clinico(texto_bruto: str) -> str:
    texto_limpo = sanitizar_texto(texto_bruto)
    resultado_ia = organizar_atendimento(texto_limpo)
    resultado_limpo = limpar_saida(resultado_ia)
    resultado_final = aplicar_regras(resultado_limpo)

    return resultado_final