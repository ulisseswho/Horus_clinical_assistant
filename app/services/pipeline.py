from app.services.atendimento_service import organizar_atendimento
from app.services.sanitizacao_service import sanitizar_texto
from app.services.pos_processamento import aplicar_regras
import re


def limpar_saida(texto: str) -> str:
    if not texto:
        return texto

    # 1. Remover hífen no início de QP e HDA
    texto = re.sub(r"(»» Queixa Principal:\s*)-\s*", r"\1", texto)
    texto = re.sub(r"(»» História da Doença Atual:\s*)-\s*", r"\1", texto)

    # 2. Padronizar espaçamento entre seções
    texto = re.sub(r"\n*»» ", r"\n\n»» ", texto)

    # 3. Remover excesso de linhas
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    # 4. Garantir apenas UMA seção de parâmetros na admissão
    secoes_parametros = re.findall(
        r"(»» Parâmetros na admissão:\s*.*?)(?=\n\n»» |\Z)",
        texto,
        flags=re.DOTALL,
    )

    if secoes_parametros:
        secao_escolhida = None

        # prefere a primeira seção com valores reais
        for secao in secoes_parametros:
            conteudo = re.sub(r"^»» Parâmetros na admissão:\s*", "", secao).strip()
            if conteudo and "PA - mmHg" not in conteudo:
                secao_escolhida = "»» Parâmetros na admissão:\n" + conteudo
                break

        # se não houver uma seção preenchida, usa a primeira ou placeholder
        if secao_escolhida is None:
            conteudo = re.sub(
                r"^»» Parâmetros na admissão:\s*",
                "",
                secoes_parametros[0],
            ).strip()

            if not conteudo or conteudo == "-":
                secao_escolhida = (
                    "»» Parâmetros na admissão:\n"
                    "PA - mmHg || FC - bpm || FR - irpm || Temp - °C || SatO2 - % || Glicemia - mg/dL"
                )
            else:
                secao_escolhida = "»» Parâmetros na admissão:\n" + conteudo

        # remove todas as seções duplicadas
        texto = re.sub(
            r"(?:\n\n)?»» Parâmetros na admissão:\s*.*?(?=\n\n»» |\Z)",
            "",
            texto,
            flags=re.DOTALL,
        ).strip()

        # recoloca a seção única antes de Exames laboratoriais, se existir
        if "»» Exames laboratoriais:" in texto:
            texto = texto.replace(
                "»» Exames laboratoriais:",
                f"{secao_escolhida}\n\n»» Exames laboratoriais:",
                1,
            )
        else:
            texto = f"{texto}\n\n{secao_escolhida}"

    # 5. Normalizar lista numerada em Condutas
    match_condutas = re.search(r"(»» Condutas:\n)(.*)", texto, re.DOTALL)
    if match_condutas:
        cabecalho = match_condutas.group(1)
        conteudo = match_condutas.group(2).strip()

        conteudo = re.sub(r"\n{2,}", "\n", conteudo)
        conteudo = re.sub(r"\s*(\d+\.\s)", r"\n\1", conteudo)
        conteudo = conteudo.lstrip()
        conteudo = re.sub(r"\n{2,}", "\n", conteudo)

        texto = re.sub(
            r"»» Condutas:\n.*",
            f"{cabecalho}{conteudo}",
            texto,
            flags=re.DOTALL,
        )

    return texto.strip()


def processar_texto_clinico(texto_bruto: str) -> str:
    texto_limpo = sanitizar_texto(texto_bruto)
    resultado_ia = organizar_atendimento(texto_limpo)
    resultado_limpo = limpar_saida(resultado_ia)
    resultado_final = aplicar_regras(resultado_limpo)
    return resultado_final