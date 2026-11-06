import re, shutil, datetime, os

# 1. Auditoria: Ver como o histórico é renderizado
print("=== AUDITORIA DE RENDERIZAÇÃO ===")
for nome in ["analise_comparativo_receitas.html", "analise_comparativo_despesas.html"]:
    caminho = os.path.join("pc_frontend", nome)
    with open(caminho, "r", encoding="utf-8") as f:
        txt = f.read()
    
    # Mostra como o histórico é carregado (procura a função carregarHistorico)
    idx = txt.find("function carregarHistorico")
    if idx != -1:
        inicio = idx
        fim = txt.find("\n    }", idx) + 6
        print(f"\n--- {nome} ---")
        print(txt[inicio:fim])
    else:
        print(f"\n--- {nome} ---\nFunção carregarHistorico não encontrada.")
