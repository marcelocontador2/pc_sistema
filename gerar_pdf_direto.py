import sys, os
sys.path.insert(0, os.path.abspath("pc_backend"))
from main import gerar_pdf_relatorio_consolidado

ID_RELATORIO = 25
resposta = gerar_pdf_relatorio_consolidado(ID_RELATORIO)
with open(f"relatorio_consolidado_{ID_RELATORIO}.pdf", "wb") as f:
    f.write(resposta.body)
print(f"✅ PDF gerado: relatorio_consolidado_{ID_RELATORIO}.pdf ({len(resposta.body)} bytes)")
