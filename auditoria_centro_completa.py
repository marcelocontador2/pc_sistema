import re
import os

print("=" * 70)
print("AUDITORIA DO RELATÓRIO DE CENTRO DE CUSTOS")
print("=" * 70)

arquivo = r"pc_frontend\relatorio_centro_custos.html"

if not os.path.exists(arquivo):
    print(f"[ERRO] Arquivo {arquivo} não encontrado.")
else:
    c = open(arquivo, encoding='utf-8').read()

    # 1. Onde está a palavra CONCLUSÃO?
    print("\n--- 1. ESTRUTURA DO TÍTULO DE CONCLUSÃO ---")
    match = re.search(r'.{0,200}CONCLUSÃO.{0,200}', c, re.DOTALL | re.IGNORECASE)
    if match:
        print(match.group(0).strip())
    else:
        print("Não encontrei a palavra CONCLUSÃO no HTML.")

    # 2. Os botões que tentamos injetar estão lá?
    print("\n--- 2. BOTÕES DE EDIÇÃO INJETADOS ---")
    if 'id="btn-edit"' in c:
        print("[OK] O botão de Editar está no HTML.")
    else:
        print("[FALTA] O botão de Editar NÃO está no HTML.")

    if 'id="toolbar-conclusao"' in c:
        print("[OK] A barra de ferramentas está no HTML.")
    else:
        print("[FALTA] A barra de ferramentas NÃO está no HTML.")

    # 3. O que o backend está chamando?
    print("\n--- 3. ROTA DO PLAYWRIGHT NO BACKEND ---")
    c_back = open(r"pc_backend\main.py", encoding='utf-8-sig').read()
    match_rota = re.search(r'url = f"http://127\.0\.0\.1:9994/(relatorio_centro_custos[^"]*)"', c_back)
    if match_rota:
        print(f"O Playwright está abrindo: /{match_rota.group(1)}")
    else:
        print("Rota não encontrada no main.py.")
