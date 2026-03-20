from app.infra.ai_client import gerar_texto
from app.services.sanitizacao_service import sanitizar_texto


def organizar_evolucao(texto_bruto: str) -> str:
    texto_bruto = sanitizar_texto(texto_bruto)

    prompt = f"""
Você é um assistente de organização clínica para médico emergencista.

Organize o texto abaixo no modelo exato:

»» Evolução Médica

»» Impressão Diagnóstica:
1. -

»» Queixa Principal:
-

»» História da Doença Atual:
-

»» Histórico Médico Pregresso:
Comorbidades: -
Cirurgias prévias: -
Alergias: -
Uso de medicamentos contínuos: -
História familiar relevante: -

»» Exame Físico:
Ectoscopia: -
Neurológico: -
Cardiovascular: -
Respiratório: -
Abdome: -
Extremidades: -

»» Parâmetros:
PA - mmHg || FC - bpm || FR - irpm || Temp - °C || SatO2 - % || Glicemia - mg/dL || Hora -

»» Evolução:
-

»» Exames laboratoriais:
-

»» Exames de imagem:
-

»» Consulta com especialidades:
-

»» Condutas:
1. -

Regras obrigatórias:
- Não usar markdown.
- Não inventar dados.
- Se faltar informação, usar "-".
- Manter linguagem médica clara, objetiva e organizada.
- Não preencher parâmetros automaticamente se eles não estiverem claros.
- Exames laboratoriais devem permanecer objetivos, sem narrativa interpretativa.
- Exames de imagem devem permanecer objetivos, sem hipóteses novas.
- Não usar hífen no início de Queixa Principal, História da Doença Atual e Evolução.
- Organizar Condutas em lista numerada.

Texto bruto:
{texto_bruto}
"""
    return gerar_texto(prompt)