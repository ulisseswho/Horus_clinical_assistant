import re
import streamlit as st

from app.infra.ai_client import gerar_texto
from app.infra.ocr_engine import extrair_texto_pdf, extrair_texto_imagem
from app.services.pipeline import processar_texto_clinico, limpar_saida
from app.services.pos_processamento import aplicar_regras
from app.services.sanitizacao_service import sanitizar_texto
from app.services.sugestoes_conduta_service import sugerir_condutas

MODELO_IA = "gpt-4.1-mini + gpt-4.1"

MANUAL_DEFAULTS = {
    "imp": "",
    "qp": "",
    "hda": "",
    "hpp": "",
    "ef": "",
    "pa": "",
    "fc": "",
    "fr": "",
    "temp": "",
    "sato2": "",
    "glicemia": "",
    "lab": "",
    "img": "",
    "pareceres": "",
    "condutas": "",
}


def paciente_factory(pid):
    return {
        "id": pid,
        "manual": MANUAL_DEFAULTS.copy(),
        "texto_colado": "",
        "texto_bruto": "",
        "texto_sanitizado": "",
        "resultado": "",
        "resultado_revisao_ia": "",
        "sugestoes": "",
        "status": "",
        "mostrar_bruto": False,
        "mostrar_sanitizado": False,
        "modo_revisao": False,
        "ultima_fonte_arquivo": "",
    }


def novo_paciente():
    salvar_campos_manuais()
    n = len(st.session_state.pacientes) + 1
    st.session_state.pacientes.append(paciente_factory(f"Paciente {n:03d}"))
    st.session_state.paciente_atual = n - 1


def widget_key(field: str, pid: str) -> str:
    return f"{field}_{pid}"


def carregar_campos_manuais(pid: str, paciente: dict):
    for field, default in MANUAL_DEFAULTS.items():
        key = widget_key(field, pid)
        if key not in st.session_state:
            st.session_state[key] = paciente["manual"].get(field, default)


def salvar_campos_manuais():
    if "pacientes" not in st.session_state or "paciente_atual" not in st.session_state:
        return

    idx = st.session_state.paciente_atual
    if idx >= len(st.session_state.pacientes):
        return

    paciente = st.session_state.pacientes[idx]
    pid = paciente["id"]

    for field in MANUAL_DEFAULTS:
        key = widget_key(field, pid)
        if key in st.session_state:
            paciente["manual"][field] = st.session_state[key]


def limpar_widgets_do_paciente(pid: str):
    chaves = [widget_key(field, pid) for field in MANUAL_DEFAULTS] + [
        f"texto_origem_input_{pid}",
        f"anexar_origem_{pid}_Atendimento Clínico",
        f"tipo_entrada_atendimento_{pid}",
        f"sugestoes_chk_origem_{pid}",
        f"sugestoes_chk_manual_{pid}",
        f"upload_atendimento_{pid}",
        f"origem_{pid}",
        f"sanitizado_{pid}",
        f"resultado_final_{pid}",
        f"sugestoes_finais_{pid}",
    ]

    for chave in chaves:
        if chave in st.session_state:
            del st.session_state[chave]


def zerar_paciente_atual():
    idx = st.session_state.paciente_atual
    pid = st.session_state.pacientes[idx]["id"]

    st.session_state.pacientes[idx] = paciente_factory(pid)
    limpar_widgets_do_paciente(pid)

    st.session_state[f"anexar_origem_{pid}_Atendimento Clínico"] = "Não"
    st.session_state[f"tipo_entrada_atendimento_{pid}"] = "Texto"


def preencher_teste_manual():
    idx = st.session_state.paciente_atual
    pid = st.session_state.pacientes[idx]["id"]

    st.session_state.pacientes[idx] = paciente_factory(pid)
    st.session_state.pacientes[idx]["manual"].update(
        {
            "imp": "sepse? foco pulmonar\ninsuf respiratoria aguda",
            "qp": "",
            "hda": (
                "PACIENTE VEM COM FEBRE HA 3 DIAS, tosse produtiva amarelada e falta de ar progressiva, "
                "pior hoje. refere calafrios, FRAQUEZA importante e um episodio de tonteira. "
                "nega dor toracica tipica. DEU entrada por piora da dispneia."
            ),
            "hpp": "has, dm2. usa losartana e metformina. nega alergias. cirurgia previa apendicectomia",
            "ef": "taquipneico, hipocorado, crepitacoes em base direita. RCR 2T. sem edema.",
            "pa": "",
            "fc": "",
            "fr": "",
            "temp": "",
            "sato2": "",
            "glicemia": "",
            "lab": "(19/03/2026): HB 10,2 | HT 30 | LEUCO 17800 | PLAQ 310000 | PCR 18,4 | NA 132 | K 4,1 | CREA 1,0",
            "img": "(19/03/2026): RX TORAX COM infiltrado em base pulmonar direita",
            "pareceres": "",
            "condutas": "internar, antibiotico EV, oxigenio, solicitar exames, parecer da pneumo",
        }
    )

    limpar_widgets_do_paciente(pid)
    carregar_campos_manuais(pid, st.session_state.pacientes[idx])
    st.session_state[f"anexar_origem_{pid}_Atendimento Clínico"] = "Não"
    st.session_state.pacientes[idx]["modo_revisao"] = True
    st.session_state.pacientes[idx]["status"] = "Teste manual carregado."


def preencher_teste_texto():
    idx = st.session_state.paciente_atual
    pid = st.session_state.pacientes[idx]["id"]

    st.session_state.pacientes[idx] = paciente_factory(pid)
    limpar_widgets_do_paciente(pid)

    st.session_state[f"anexar_origem_{pid}_Atendimento Clínico"] = "Sim"
    st.session_state[f"tipo_entrada_atendimento_{pid}"] = "Texto"

    texto_teste = """
HOSPITAL XPTO
NOME: JOANA PEREIRA DA COSTA
CPF: 12345678900
MAE: MARIA PEREIRA
TELEFONE: 85999999999

PACIENTE FEMININA 47 ANOS CHEGA COM FEBRE, TOSSE E CANSACO IMPORTANTE HÁ 4 DIAS.
HOJE PIOROU COM FALTA DE AR. NEGA DOR TORACICA TIPICA.
HAS E DM2. usa LOSARTANA e metformina. nega alergias. fez colecistectomia.

EXAME FISICO:
hipocorada, taquipneica, crepitacoes em base direita, RCR 2T sem sopros, abdome flacido, sem edema.

LABS:
(19/03/2026): HB 9,8 | HT 29 | LEUCO 18200 | PLAQ 290000 | PCR 22 | NA 131 | K 4,3 | CREA 1,1

IMAGEM:
(19/03/2026): RX TORAX com infiltrado em base pulmonar direita

CONDUTAS:
internar, antibiotico ev, oxigenio, solicitar exames, parecer da pneumo
""".strip()

    st.session_state.pacientes[idx]["texto_colado"] = texto_teste
    st.session_state[f"texto_origem_input_{pid}"] = texto_teste
    st.session_state.pacientes[idx]["status"] = "Teste em modo texto carregado."


def extrair_texto_arquivo(arquivo) -> str:
    if arquivo.type == "application/pdf":
        return extrair_texto_pdf(arquivo)
    return extrair_texto_imagem(arquivo)


def extrair_secao(texto: str, cabecalho: str, proximos: list[str]) -> str:
    padrao_cabecalho = re.escape(cabecalho)
    padrao_proximos = "|".join(re.escape(x) for x in proximos)
    padrao = rf"{padrao_cabecalho}\s*(.*?)(?=\n(?:{padrao_proximos})|\Z)"
    m = re.search(padrao, texto, flags=re.DOTALL)
    if not m:
        return ""
    return m.group(1).strip()


def preencher_manual_a_partir_do_texto_organizado(texto: str, paciente: dict):
    headers = {
        "imp": "»» Impressão Diagnóstica:",
        "qp": "»» Queixa Principal:",
        "hda": "»» História da Doença Atual:",
        "hpp": "»» Histórico Médico Pregresso:",
        "ef": "»» Exame Físico:",
        "lab": "»» Exames laboratoriais:",
        "img": "»» Exames de imagem:",
        "pareceres": "»» Pareceres:",
        "condutas": "»» Condutas:",
    }

    ordem = list(headers.values())

    for campo, cabecalho in headers.items():
        proximos = [h for h in ordem if h != cabecalho]
        secao = extrair_secao(texto, cabecalho, proximos)

        if campo == "imp":
            secao = re.sub(r"^\d+\.\s*", "", secao, flags=re.MULTILINE).strip()

        paciente["manual"][campo] = secao

    paciente["manual"]["pa"] = ""
    paciente["manual"]["fc"] = ""
    paciente["manual"]["fr"] = ""
    paciente["manual"]["temp"] = ""
    paciente["manual"]["sato2"] = ""
    paciente["manual"]["glicemia"] = ""


def renumerar_secao(texto: str, titulo_secao: str) -> str:
    padrao = rf"({re.escape(titulo_secao)}\n)(.*?)(?=\n\n»» |\Z)"
    match = re.search(padrao, texto, re.DOTALL)

    if not match:
        return texto

    cabecalho = match.group(1)
    conteudo = match.group(2).strip()

    if not conteudo:
        return texto

    linhas = [linha.strip() for linha in conteudo.split("\n") if linha.strip()]
    linhas_limpa = []

    for linha in linhas:
        linha = re.sub(r"^\d+\.\s*", "", linha).strip()
        linha = re.sub(r"^[-•]\s*", "", linha).strip()
        if linha:
            linhas_limpa.append(linha)

    if not linhas_limpa:
        return texto

    conteudo_novo = "\n".join(f"{i}. {linha}" for i, linha in enumerate(linhas_limpa, 1))

    texto = re.sub(
        padrao,
        f"{cabecalho}{conteudo_novo}",
        texto,
        flags=re.DOTALL,
    )

    return texto


def refinar_texto_final(texto: str) -> str:
    prompt = f"""
Você é um médico com excelente redação técnica.

Reescreva o texto abaixo em linguagem médica formal, clara e elegante.

Regras obrigatórias:
- Não inventar informações.
- Não remover informações clínicas relevantes.
- Não alterar valores numéricos.
- Não alterar parâmetros vitais ou laboratoriais.
- Não alterar diagnósticos.
- Não alterar a estrutura das seções iniciadas por »».
- Apenas melhorar gramática, formalidade e clareza.
- A seção »» Impressão Diagnóstica: deve permanecer numerada, com um item por linha.
- A seção »» Condutas: deve permanecer numerada, com um item por linha.
- Não transformar Impressão Diagnóstica em parágrafo.
- Não transformar Condutas em parágrafo.
- Em Condutas, transforme frases telegráficas em formulações médicas formais.

Texto:
{texto}
"""
    try:
        resposta = gerar_texto(prompt, modelo="gpt-4.1")
        return resposta if resposta else texto
    except Exception:
        return texto


st.set_page_config(page_title="HORUS CLINICAL ASSISTANT", layout="wide")

if "pacientes" not in st.session_state:
    st.session_state.pacientes = [paciente_factory("Paciente 001")]

if "paciente_atual" not in st.session_state:
    st.session_state.paciente_atual = 0

with st.sidebar:
    st.subheader("Pacientes")

    nomes = [p["id"] for p in st.session_state.pacientes]

    selecionado = st.selectbox(
        "Paciente atual",
        options=list(range(len(nomes))),
        format_func=lambda i: nomes[i],
        index=st.session_state.paciente_atual,
    )

    if selecionado != st.session_state.paciente_atual:
        salvar_campos_manuais()
        st.session_state.paciente_atual = selecionado
        st.rerun()

    pid_sidebar = st.session_state.pacientes[st.session_state.paciente_atual]["id"]
    anexar_atual = st.session_state.get(
        f"anexar_origem_{pid_sidebar}_Atendimento Clínico", "Não"
    )
    tipo_atual = st.session_state.get(
        f"tipo_entrada_atendimento_{pid_sidebar}", "Texto"
    )

    if st.button("Novo paciente", use_container_width=True):
        novo_paciente()
        st.rerun()

    if st.button("Zerar atendimento", use_container_width=True):
        zerar_paciente_atual()
        st.rerun()

    teste_desativado = anexar_atual == "Sim" and tipo_atual == "Arquivo"

    if st.button("Teste", use_container_width=True, disabled=teste_desativado):
        if anexar_atual == "Não":
            preencher_teste_manual()
        elif anexar_atual == "Sim" and tipo_atual == "Texto":
            preencher_teste_texto()
        st.rerun()

    if teste_desativado:
        st.caption("Teste desativado no modo Sim + Arquivo.")

indice_paciente = st.session_state.paciente_atual
paciente = st.session_state.pacientes[indice_paciente]
pid = paciente["id"]

st.title("HORUS CLINICAL ASSISTANT")
st.caption(
    "Ferramenta para extração, sanitização e organização de atendimentos clínicos. "
    "Os identificadores diretos são removidos antes do processamento."
)
st.caption(f"Modelo de IA: {MODELO_IA}")

st.markdown("### PASSO 01: Qual modelo deseja?")
modelo = st.selectbox("", ["Atendimento Clínico"], label_visibility="collapsed")

st.markdown("### PASSO 02: Anexar documentos da origem?")
anexar_origem = st.radio(
    "",
    ["Não", "Sim"],
    horizontal=True,
    label_visibility="collapsed",
    key=f"anexar_origem_{pid}_{modelo}",
)

if modelo == "Atendimento Clínico":
    if anexar_origem == "Sim":
        tipo_entrada = st.radio(
            "Origem do documento",
            ["Texto", "Arquivo"],
            horizontal=True,
            key=f"tipo_entrada_atendimento_{pid}",
        )

        if tipo_entrada == "Texto":
            texto_key = f"texto_origem_input_{pid}"
            if texto_key not in st.session_state:
                st.session_state[texto_key] = st.session_state.pacientes[indice_paciente].get(
                    "texto_colado", ""
                )

            texto_entrada = st.text_area(
                "Texto Bruto",
                height=220,
                key=texto_key,
            )

            if texto_entrada.strip():
                if st.button(
                    "Sanitizar",
                    use_container_width=True,
                    key=f"btn_sanitizar_texto_{pid}",
                ):
                    bruto = texto_entrada.strip()
                    texto_sanitizado = sanitizar_texto(bruto)

                    st.session_state.pacientes[indice_paciente]["texto_colado"] = bruto
                    st.session_state.pacientes[indice_paciente]["texto_bruto"] = bruto
                    st.session_state.pacientes[indice_paciente]["texto_sanitizado"] = texto_sanitizado
                    st.session_state.pacientes[indice_paciente]["mostrar_bruto"] = True
                    st.session_state.pacientes[indice_paciente]["mostrar_sanitizado"] = True
                    st.session_state.pacientes[indice_paciente]["modo_revisao"] = False
                    st.session_state.pacientes[indice_paciente]["resultado"] = ""
                    st.session_state.pacientes[indice_paciente]["sugestoes"] = ""
                    st.session_state.pacientes[indice_paciente]["status"] = "Texto sanitizado com sucesso."
                    st.rerun()

                if st.session_state.pacientes[indice_paciente].get("mostrar_sanitizado", False):
                    st.markdown("### Texto Sanitizado")
                    st.text_area(
                        "",
                        value=st.session_state.pacientes[indice_paciente].get("texto_sanitizado", ""),
                        height=220,
                        key=f"sanitizado_{pid}",
                        label_visibility="collapsed",
                        disabled=True,
                    )

                    if st.button(
                        "Revisar",
                        use_container_width=True,
                        key=f"btn_revisar_texto_{pid}",
                    ):
                        texto_sanitizado = st.session_state.pacientes[indice_paciente].get(
                            "texto_sanitizado", ""
                        ).strip()

                        if texto_sanitizado:
                            with st.spinner("Organizando conteúdo para revisão..."):
                                texto_organizado = processar_texto_clinico(texto_sanitizado)

                            st.session_state.pacientes[indice_paciente]["resultado_revisao_ia"] = texto_organizado

                            preencher_manual_a_partir_do_texto_organizado(
                                texto_organizado,
                                st.session_state.pacientes[indice_paciente],
                            )

                            limpar_widgets_do_paciente(pid)
                            carregar_campos_manuais(pid, st.session_state.pacientes[indice_paciente])

                            st.session_state.pacientes[indice_paciente]["modo_revisao"] = True
                            st.session_state.pacientes[indice_paciente]["status"] = "Campos de revisão preenchidos."
                            st.rerun()

        else:
            arquivo = st.file_uploader(
                "Envie PDF ou imagem",
                type=["pdf", "png", "jpg", "jpeg"],
                key=f"upload_atendimento_{pid}",
            )

            if arquivo is not None:
                st.markdown("### Arquivo selecionado")
                st.caption(getattr(arquivo, "name", "Arquivo"))

                if st.button(
                    "Extrair",
                    use_container_width=True,
                    key=f"btn_extrair_arquivo_{pid}",
                ):
                    texto_extraido = extrair_texto_arquivo(arquivo)
                    st.session_state.pacientes[indice_paciente]["texto_bruto"] = texto_extraido
                    st.session_state.pacientes[indice_paciente]["texto_sanitizado"] = ""
                    st.session_state.pacientes[indice_paciente]["ultima_fonte_arquivo"] = getattr(arquivo, "name", "")
                    st.session_state.pacientes[indice_paciente]["mostrar_bruto"] = True
                    st.session_state.pacientes[indice_paciente]["mostrar_sanitizado"] = False
                    st.session_state.pacientes[indice_paciente]["modo_revisao"] = False
                    st.session_state.pacientes[indice_paciente]["resultado"] = ""
                    st.session_state.pacientes[indice_paciente]["sugestoes"] = ""
                    st.session_state.pacientes[indice_paciente]["status"] = "Texto extraído com sucesso."
                    st.rerun()

            if st.session_state.pacientes[indice_paciente].get("mostrar_bruto", False):
                st.markdown("### Texto Bruto")
                st.text_area(
                    "",
                    value=st.session_state.pacientes[indice_paciente].get("texto_bruto", ""),
                    height=260,
                    key=f"origem_{pid}",
                    label_visibility="collapsed",
                    disabled=True,
                )

                if st.button(
                    "Sanitizar",
                    use_container_width=True,
                    key=f"btn_sanitizar_arquivo_{pid}",
                ):
                    bruto = st.session_state.pacientes[indice_paciente].get("texto_bruto", "").strip()

                    if bruto:
                        texto_sanitizado = sanitizar_texto(bruto)
                        st.session_state.pacientes[indice_paciente]["texto_sanitizado"] = texto_sanitizado
                        st.session_state.pacientes[indice_paciente]["mostrar_sanitizado"] = True
                        st.session_state.pacientes[indice_paciente]["modo_revisao"] = False
                        st.session_state.pacientes[indice_paciente]["resultado"] = ""
                        st.session_state.pacientes[indice_paciente]["sugestoes"] = ""
                        st.session_state.pacientes[indice_paciente]["status"] = "Texto sanitizado com sucesso."
                    else:
                        st.session_state.pacientes[indice_paciente]["status"] = "Nenhum texto para sanitizar."
                    st.rerun()

            if st.session_state.pacientes[indice_paciente].get("mostrar_sanitizado", False):
                st.markdown("### Texto Sanitizado")
                st.text_area(
                    "",
                    value=st.session_state.pacientes[indice_paciente].get("texto_sanitizado", ""),
                    height=220,
                    key=f"sanitizado_{pid}",
                    label_visibility="collapsed",
                    disabled=True,
                )

                if st.button(
                    "Revisar",
                    use_container_width=True,
                    key=f"btn_revisar_arquivo_{pid}",
                ):
                    texto_sanitizado = st.session_state.pacientes[indice_paciente].get(
                        "texto_sanitizado", ""
                    ).strip()

                    if texto_sanitizado:
                        with st.spinner("Organizando conteúdo para revisão..."):
                            texto_organizado = processar_texto_clinico(texto_sanitizado)

                        st.session_state.pacientes[indice_paciente]["resultado_revisao_ia"] = texto_organizado

                        preencher_manual_a_partir_do_texto_organizado(
                            texto_organizado,
                            st.session_state.pacientes[indice_paciente],
                        )

                        limpar_widgets_do_paciente(pid)
                        carregar_campos_manuais(pid, st.session_state.pacientes[indice_paciente])

                        st.session_state.pacientes[indice_paciente]["modo_revisao"] = True
                        st.session_state.pacientes[indice_paciente]["status"] = "Campos de revisão preenchidos."
                    else:
                        st.session_state.pacientes[indice_paciente]["status"] = "Sanitize antes de revisar."
                    st.rerun()

    if anexar_origem == "Não" or paciente.get("modo_revisao", False):
        carregar_campos_manuais(pid, paciente)

        st.markdown("### Estrutura do Atendimento")

        imp = st.text_area("Impressões diagnósticas", height=120, key=widget_key("imp", pid))
        qp = st.text_area("Queixa", height=80, key=widget_key("qp", pid))
        hda = st.text_area("HDA", height=160, key=widget_key("hda", pid))
        hpp = st.text_area("HPP", height=140, key=widget_key("hpp", pid))
        exame_fisico = st.text_area("Exame Físico", height=220, key=widget_key("ef", pid))

        st.markdown("#### Parâmetros")
        c1, c2, c3, c4, c5, c6 = st.columns(6)

        pa = c1.text_input("PA", key=widget_key("pa", pid))
        fc = c2.text_input("FC", key=widget_key("fc", pid))
        fr = c3.text_input("FR", key=widget_key("fr", pid))
        temp = c4.text_input("Temp", key=widget_key("temp", pid))
        sato2 = c5.text_input("SatO2", key=widget_key("sato2", pid))
        glicemia = c6.text_input("Glicemia", key=widget_key("glicemia", pid))

        exames_lab = st.text_area("Exames laboratoriais", height=140, key=widget_key("lab", pid))
        exames_img = st.text_area("Exames de imagem", height=140, key=widget_key("img", pid))
        pareceres = st.text_area("Pareceres", height=120, key=widget_key("pareceres", pid))
        condutas = st.text_area("Condutas", height=180, key=widget_key("condutas", pid))

        salvar_campos_manuais()

        gerar_sug = st.checkbox(
            "Sugestões de conduta",
            value=False,
            key=f"sugestoes_chk_manual_{pid}",
        )

        if st.button(
            "Gerar atendimento",
            use_container_width=True,
            key=f"btn_gerar_atendimento_manual_{pid}",
        ):
            parametros = (
                f"PA {pa if pa else '-'} mmHg || "
                f"FC {fc if fc else '-'} bpm || "
                f"FR {fr if fr else '-'} irpm || "
                f"Temp {temp if temp else '-'} °C || "
                f"SatO2 {sato2 if sato2 else '-'} % || "
                f"Glicemia {glicemia if glicemia else '-'} mg/dL"
            )

            texto_base = f"""
»» Impressão Diagnóstica:
{imp}

»» Queixa Principal:
{qp}

»» História da Doença Atual:
{hda}

»» Histórico Médico Pregresso:
{hpp}

»» Exame Físico:
{exame_fisico}

»» Parâmetros na admissão:
{parametros}

»» Exames laboratoriais:
{exames_lab}

»» Exames de imagem:
{exames_img}

»» Pareceres:
{pareceres}

»» Condutas:
{condutas}
"""

            with st.spinner("Gerando atendimento..."):
                texto_estruturado = aplicar_regras(limpar_saida(texto_base))
                res = refinar_texto_final(texto_estruturado)
                res = aplicar_regras(limpar_saida(res))
                res = renumerar_secao(res, "»» Impressão Diagnóstica:")
                res = renumerar_secao(res, "»» Condutas:")

            st.session_state.pacientes[indice_paciente]["resultado"] = res
            st.session_state.pacientes[indice_paciente]["status"] = "Atendimento gerado com sucesso."

            if gerar_sug:
                with st.spinner("Gerando sugestões de conduta..."):
                    st.session_state.pacientes[indice_paciente]["sugestoes"] = sugerir_condutas(res)
            else:
                st.session_state.pacientes[indice_paciente]["sugestoes"] = ""

            st.rerun()

status_atual = st.session_state.pacientes[indice_paciente].get("status", "")
resultado_atual = st.session_state.pacientes[indice_paciente].get("resultado", "")
sugestoes_atuais = st.session_state.pacientes[indice_paciente].get("sugestoes", "")

if status_atual:
    st.info(status_atual)

if resultado_atual:
    st.markdown("### Resultado")
    st.text_area(
        "Resultado final",
        resultado_atual,
        height=420,
        label_visibility="collapsed",
    )

if sugestoes_atuais:
    st.markdown("### Sugestões")
    st.text_area(
        "Sugestões finais",
        sugestoes_atuais,
        height=220,
        label_visibility="collapsed",
    )