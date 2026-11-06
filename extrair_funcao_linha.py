import re

arq = r"pc_backend\main.py"
with open(arq, "r", encoding="utf-8") as f:
    linhas = f.readlines()

with open("trecho_funcao_linha.txt", "w", encoding="utf-8") as out:
    dentro_da_funcao = False
    for i, linha in enumerate(linhas):
        if "def linha(" in linha:
            dentro_da_funcao = True
        if dentro_da_funcao:
            out.write(f"{i+1}: {linha}")
            # Se a linha começar com '    ' ou 'def ', continua. Se for uma linha vazia seguida de outra coisa, para.
            if linha.strip() == "" and i > 0 and not linhas[i-1].startswith(" "):
                break
            if "pdf.cell" in linha or "pdf.set_font" in linha:
                pass

print("[OK] Função extraída para 'trecho_funcao_linha.txt'")
