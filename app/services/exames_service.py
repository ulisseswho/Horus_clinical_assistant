from app.infra.ai_client import gerar_texto
from app.services.sanitizacao_service import sanitizar_texto


def organizar_exames(texto_bruto: str) -> str:
    texto_bruto = sanitizar_texto(texto_bruto)

    prompt = f"""
Você é um assistente de organização de exames complementares.

Organize o texto abaixo no modelo exato:

»» Exames Complementares

»» Exames laboratoriais:
-

»» Exames de imagem:
-

Regras obrigatórias:
- Não usar markdown.
- Não inventar dados.
- Se faltar informação, usar "-".
- Em exames laboratoriais, usar datas antes dos resultados sempre que existirem.
- Em exames laboratoriais, não interpretar, não resumir em hipóteses e não criar narrativa clínica.
- Em exames laboratoriais, usar apenas resultados objetivos.
- Pode agrupar por categorias como Hemograma, Coagulação, Bioquímica, Eletrólitos, Função renal, Função tireoidiana, Marcadores inflamatórios, Reticulócitos, Sorologias, Imunologia e Outros.
- Em exames de imagem, organizar apenas achados e resultados objetivos, sem criar hipótese diagnóstica nova.
- Preservar datas e horários quando existirem no texto.

Texto bruto:
{texto_bruto}
"""
    return gerar_texto(prompt)