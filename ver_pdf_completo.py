from pathlib import Path

arquivo = Path("pc_frontend/custo_pessoal_pdf_completo.html")
conteudo = arquivo.read_text(encoding="utf-8")

# Mostrar as linhas 90 a 130 (onde esta o script)
linhas = conteudo.splitlines()
print("=== PDF COMPLETO (linhas 90 a 140) ===")
for i in range(89, min(140, len(linhas))):
    if linhas[i].strip():
        print(f"{i+1:4d}  {linhas[i]}")
