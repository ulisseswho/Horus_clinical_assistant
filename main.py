from app.services.pipeline import processar_texto_clinico
from app.services.sugestoes_conduta_service import sugerir_condutas
from app.infra.ocr_engine import extrair_texto_pdf

with open("arquivos/teste.pdf", "rb") as f:
    texto = extrair_texto_pdf(f)

atendimento = processar_texto_clinico(texto)

print(atendimento)
print("\n")
print(sugerir_condutas(atendimento))