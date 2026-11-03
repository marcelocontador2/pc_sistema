import re, os

print("=" * 70)
print("DIAGNÓSTICO: ROTA DO PANORAMA")
print("=" * 70)

# 1. Ver como a rota foi criada no backend
c_back = open(r"pc_backend\main.py", encoding="utf-8-sig").read()
match_rota = re.search(r'(@app\.get\("/gerar_pdf_panorama/\{historico_id\}"\).*?)(?=\n@app\.|\Z)', c_back, re.DOTALL)
if match_rota:
    print("\n--- CÓDIGO DA ROTA NO BACKEND ---")
    print(match_rota.group(1).strip()[:1000])
else:
    print("\n[AVISO] Rota /gerar_pdf_panorama/{historico_id} não encontrada no main.py")

# 2. Verificar se existe o arquivo de relatório
print("\n--- ARQUIVOS DE RELATÓRIO NA PASTA ---")
for f in os.listdir("pc_frontend"):
    if "relatorio" in f.lower() and "panorama" in f.lower():
        print(f" - {f}")

# 3. Verificar como a tela panorama.html salva o histórico
print("\n--- COMO O PANORAMA SALVA O HISTÓRICO ---")
c_pano = open(r"pc_frontend\panorama.html", encoding="utf-8").read()
match_save = re.search(r'fetch\([^)]*(?:salvar|historico)[^)]*\)', c_pano, re.IGNORECASE)
if match_save:
    print(f"Chamada de salvar encontrada: {match_save.group(0)}")
else:
    print("Não encontrei chamada de salvar histórico no panorama.html")
