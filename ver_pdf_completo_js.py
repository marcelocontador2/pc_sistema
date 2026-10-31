from pathlib import Path

arquivo = Path("pc_frontend/custo_pessoal_pdf_completo.html")
conteudo = arquivo.read_text(encoding="utf-8")

linhas = conteudo.splitlines()
print("=== PDF COMPLETO (linhas 92 a 160) ===")
for i in range(91, min(160, len(linhas))):
    if linhas[i].strip():
        print(f"{i+1:4d}  {linhas[i]}")
