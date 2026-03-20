import re


PADROES_LINHA_REMOVER = [
    r"(?i)registro do atendimento ambulatorial",
    r"(?i)identifica[cç][aã]o paciente/cadastro",
    r"(?i)cart[aã]o nacional de sa[uú]de",
    r"(?i)\bcns\b",
    r"(?i)\bprontu[aá]rio\b",
    r"(?i)\badmiss[aã]o\b",
    r"(?i)^nome\s*:",
    r"(?i)^cpf\s*:",
    r"(?i)datanasc",
    r"(?i)data\s*de\s*nasc",
    r"(?i)\bidade\b",
    r"(?i)\bsexo\b",
    r"(?i)^m[aã]e\s*:",
    r"(?i)\btelefone\b",
    r"(?i)\bcep\b",
    r"(?i)\bbairro\b",
    r"(?i)endere[gcç]o",
    r"(?i)^profissional\s*:",
    r"(?i)\bcrm\b",
    r"(?i)n[°º]?\s*atendimento",
    r"(?i)destino interno",
    r"(?i)^#\s*id\s*:",
    r"(?i)^rua\s+betel",
    r"(?i)^unidade mantida com recursos p[uú]blicos",
    r"(?i)^exame\s*$",
    r"(?i)^prescri[cç][aã]o\s*$",
    r"(?i)^nome\s+data\s+solicita",
    r"(?i)^hospital universit[aá]rio",
    r"(?i)^hospital cear[aá]",
    r"(?i)^universit[aá]rio governo do estado",
    r"(?i)^organiza",
    r"(?i)^instituto de sa[uú]de e gest[aã]o hospitalar",
]


def _normalizar_espacos(texto: str) -> str:
    texto = texto.replace("\r", "\n")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def sanitizar_texto(texto: str) -> str:
    if not texto:
        return ""

    texto = _normalizar_espacos(texto)

    linhas_limpas = []

    for linha in texto.split("\n"):
        linha = linha.strip()

        if not linha:
            continue

        if any(re.search(padrao, linha) for padrao in PADROES_LINHA_REMOVER):
            continue

        if re.fullmatch(r"\d+", linha):
            continue

        linha = re.sub(r"(?i)^atendimento\s*$", "", linha).strip()
        linha = re.sub(r"(?i)^hda/exame f[ií]sico:\s*$", "", linha).strip()

        # remove identificadores inline
        linha = re.sub(r"(?i)nome\s*:\s*.*", "", linha).strip()
        linha = re.sub(r"(?i)cpf\s*:\s*.*", "", linha).strip()
        linha = re.sub(r"(?i)m[aã]e\s*:\s*.*", "", linha).strip()
        linha = re.sub(r"(?i)telefone\s*:\s*.*", "", linha).strip()
        linha = re.sub(r"(?i)endere[cç]o\s*:\s*.*", "", linha).strip()
        linha = re.sub(r"(?i)bairro\s*:\s*.*", "", linha).strip()
        linha = re.sub(r"(?i)cep\s*:\s*.*", "", linha).strip()
        linha = re.sub(r"(?i)cart[aã]o nacional de sa[uú]de.*", "", linha).strip()
        linha = re.sub(r"(?i)\bcns\b.*", "", linha).strip()
        linha = re.sub(r"(?i)\bprontu[aá]rio\b.*", "", linha).strip()
        linha = re.sub(r"(?i)\badmiss[aã]o\b.*", "", linha).strip()
        linha = re.sub(r"(?i)datanasc\.*.*", "", linha).strip()
        linha = re.sub(r"(?i)data\s*de\s*nasc\.*.*", "", linha).strip()
        linha = re.sub(r"(?i)\bidade\b.*", "", linha).strip()
        linha = re.sub(r"(?i)\bsexo\b.*", "", linha).strip()
        linha = re.sub(r"(?i)^profissional\s*:.*", "", linha).strip()
        linha = re.sub(r"(?i)\bcrm\b.*", "", linha).strip()
        linha = re.sub(r"(?i)n[°º]?\s*atendimento.*", "", linha).strip()
        linha = re.sub(r"(?i)destino interno\s*:.*", "", linha).strip()

        # remove CPFs soltos, com ou sem pontuação
        linha = re.sub(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", "", linha).strip()

        # remove linha de identificação resumida
        linha = re.sub(r"(?i)^#\s*id\s*:.*", "", linha).strip()
        linha = re.sub(r"(?i)^#\s*id\s*:.*?(?=#|$)", "", linha).strip()

        if not linha or len(linha) <= 1:
            continue

        linhas_limpas.append(linha)

    texto_final = "\n".join(linhas_limpas)
    texto_final = _normalizar_espacos(texto_final)

    return texto_final