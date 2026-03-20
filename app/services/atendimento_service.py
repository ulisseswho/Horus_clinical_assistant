from app.infra.ai_client import gerar_texto


def organizar_atendimento(texto_bruto: str) -> str:
    prompt = f"""
Você é um assistente de organização clínica para médico emergencista.

Organize o texto abaixo no modelo exato:

»» Atendimento Clínico

»» Impressão Diagnóstica:
1. -

»» Queixa Principal:
-

»» História da Doença Atual:
-

»» Histórico Médico Pregresso:
Comorbidades: -
Alergias: -
Uso de medicamentos contínuos: -
Cirurgias prévias: -

»» Exame Físico:
Ectoscopia: -
Neurológico: -
Cardiovascular: -
Respiratório: -
Abdome: -
Extremidades: -

»» Parâmetros na admissão:
PA - mmHg || FC - bpm || FR - irpm || Temp - °C || SatO2 - % || Glicemia - mg/dL

»» Exames laboratoriais:
-

»» Exames de imagem:
-

»» Pareceres:
-

»» Condutas:
1. -

Regras obrigatórias gerais:
- Não usar markdown.
- Não inventar dados.
- Se faltar informação, usar "-".
- Manter linguagem médica clara, objetiva e organizada.
- Preservar a lógica de atendimento inicial com dados oriundos de documentos prévios quando houver.

Queixa principal e História da Doença Atual:
- Não iniciar com hífen.
- Não usar lista.
- Escrever em texto corrido.
- A queixa principal deve ser curta e objetiva.
- A História da Doença Atual deve ser organizada em texto corrido, cronológico e clínico.

Parâmetros:
- Os parâmetros na admissão devem permanecer exatamente assim, sem preenchimento automático:
PA - mmHg || FC - bpm || FR - irpm || Temp - °C || SatO2 - % || Glicemia - mg/dL
- Nunca preencher os parâmetros a partir do texto bruto.
- Nunca inferir parâmetros.

Histórico Médico Pregresso:
- Organizar exatamente em:
Comorbidades:
Alergias:
Uso de medicamentos contínuos:
Cirurgias prévias:
- Se não houver informação em algum item, usar "-".

Exame Físico:
- Organizar exatamente em:
Ectoscopia:
Neurológico:
Cardiovascular:
Respiratório:
Abdome:
Extremidades:
- Analisar todo o texto antes de preencher os campos.
- Quando um sistema não estiver explicitamente descrito, preencher com um padrão normal coerente com o contexto clínico global.
- Nunca usar padrão normal que contradiga o caso clínico.
- Exemplo: se o paciente estiver intubado, sedado, torporoso, com rebaixamento importante do nível de consciência ou Glasgow reduzido, não escrever "Glasgow 15", "consciente e orientado" ou equivalente.
- Exemplo: se houver insuficiência respiratória, não escrever "eupneico".
- Achados respiratórios devem ficar apenas em Respiratório.
- Não duplicar achados respiratórios em Cardiovascular.
- Não duplicar o mesmo achado em sistemas diferentes.

Padrão normal contextualizado quando compatível com o caso:
- Ectoscopia: estado geral regular, afebril, acianótico, anictérico, normocorado, hidratado.
- Neurológico: Glasgow 15, pupilas isocóricas e fotorreativas, sem déficits neurológicos focais aparentes.
- Cardiovascular: bulhas rítmicas normofonéticas em 2 tempos, sem sopros, pulsos periféricos palpáveis, perfusão periférica preservada.
- Respiratório: murmúrio vesicular presente bilateralmente, sem ruídos adventícios.
- Abdome: plano, flácido, indolor à palpação, sem sinais de irritação peritoneal.
- Extremidades: sem edema, sem cianose, perfusão periférica preservada.

Exames laboratoriais:
- Não fazer narrativa clínica.
- Não resumir em hipóteses diagnósticas.
- Não interpretar.
- Não escrever frases como "anemia grave", "sem evidência", "compatível com", "sugestivo de", "persistente" ou equivalentes.
- Mostrar apenas resultados objetivos.
- Sempre colocar a data antes dos resultados.
- Quando houver hora explícita, usar:
[DD/MM/AAAA - HH:MM] Categoria: resultado || resultado || resultado
- Quando não houver hora explícita, usar:
[DD/MM/AAAA] Categoria: resultado || resultado || resultado
- Não usar o formato "(DD/MM): ...".
- Não usar lista com hífen.
- Pode agrupar por categorias como:
Hemograma
Coagulação
Bioquímica
Eletrólitos
Função renal
Função tireoidiana
Marcadores inflamatórios
Reticulócitos
Sorologias
Imunologia
Gasometria
Outros
- Usar siglas consagradas com capitalização clínica adequada, por exemplo:
Hb, Ht, VCM, HCM, CHCM, RDW, Leuco, Neut, Linf, Plaq, PCR, LDH, INR, TTPA, Na, K, Mg, Crea, Ur
- Não usar caixa alta desnecessária como HB, HT, LEUCO.
- Quando houver alteração evidente, só permitir os qualificadores finais:
(Elevado)
(Reduzido)
- Não inventar unidades.
- Preservar datas e horários quando existirem no texto de origem.
- Se não houver data legível para determinado exame, não inventar.

Exames de imagem:
- Organizar apenas resultados e achados descritos.
- Não criar hipótese diagnóstica nova.
- Não interpretar além do que está escrito.
- Preservar data e hora quando existirem.

Pareceres:
- Só preencher este campo se houver parecer real de outra especialidade explicitamente descrito no texto.
- Não transformar impressão diagnóstica, avaliação do caso, hipótese, conclusão clínica ou inferência da IA em parecer.
- Quando houver parecer real, usar o formato:
[DATA - HORA] Especialidade: conteúdo
- Se não houver parecer real, manter:
-

Condutas:
- Organizar em lista numerada.
- Melhorar a redação apenas para clareza e objetividade, sem inventar condutas não descritas.

Texto bruto:
{texto_bruto}
"""
    return gerar_texto(prompt)