import re


MAPA_ESPECIALIDADES = {
    "hemato": "Hematologia",
    "neuro": "Neurologia",
    "cardio": "Cardiologia",
    "nefro": "Nefrologia",
    "gastro": "Gastroenterologia",
    "infecto": "Infectologia",
    "dermato": "Dermatologia",
    "cirurgia": "Cirurgia Geral",
    "coloprocto": "Coloproctologia",
}


def extrair_condutas(texto: str):
    match = re.search(r"»» Condutas:(.*)", texto, re.DOTALL)
    return match.group(1).lower() if match else ""


def detectar_pareceres(condutas: str):
    encontrados = []

    for chave, nome in MAPA_ESPECIALIDADES.items():
        if chave in condutas:
            encontrados.append(nome)

    return list(set(encontrados))


def aplicar_regras(texto: str):
    condutas = extrair_condutas(texto)

    if "»» Pareceres:\n-" in texto:
        especialidades = detectar_pareceres(condutas)

        if especialidades:
            bloco = "\n".join(
                [f"Solicitado parecer da {esp}." for esp in especialidades]
            )
            texto = texto.replace("»» Pareceres:\n-", f"»» Pareceres:\n{bloco}")

    if "»» Exames laboratoriais:\n-" in texto:
        if "exame" in condutas or "laboratorial" in condutas:
            texto = texto.replace(
                "»» Exames laboratoriais:\n-",
                "»» Exames laboratoriais:\n(Solicitados)"
            )

    if "»» Exames de imagem:\n-" in texto:
        if any(x in condutas for x in ["tc", "tomografia", "rx", "raio", "usg", "resson"]):
            texto = texto.replace(
                "»» Exames de imagem:\n-",
                "»» Exames de imagem:\n(Solicitados)"
            )

    return texto