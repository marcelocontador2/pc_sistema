import re, os

print("=" * 70)
print("1. FRONTEND: COMO O BOTÃO PDF MONTA A URL")
print("=" * 70)

c = open(r"pc_frontend\index.html", encoding='utf-8').read()

# Mostra a função gerarPdfLista
idx = c.find('function gerarPdfLista')
if idx != -1:
    fim = c.find('}', idx) + 1
    print(c[idx:fim])
else:
    print("[AVISO] Função gerarPdfLista não encontrada")

# Mostra o botão PDF na tabela
idx2 = c.find('onclick="gerarPdfLista')
if idx2 != -1:
    print("\n--- BOTÃO NA TABELA ---")
    print(c[max(0,idx2-200):idx2+200])

print("\n" + "=" * 70)
print("2. BACKEND: ROTAS DE PDF DISPONÍVEIS")
print("=" * 70)

c_back = open(r"pc_backend\main.py", encoding='utf-8-sig').read()

# Lista todas as rotas de PDF
rotas = re.findall(r'@app\.get\(["\'](/[^"\']*(?:pdf|PDF)[^"\']*)["\']\)', c_back)
for rota in sorted(set(rotas)):
    print(f"  {rota}")

print("\n" + "=" * 70)
print("3. ARQUIVOS NA PASTA uploads_raw (tipo por nome)")
print("=" * 70)

pasta = r"pc_storage\uploads_raw"
if os.path.exists(pasta):
    for f in sorted(os.listdir(pasta)):
        if f.endswith('.csv'):
            # Extrai o tipo (parte antes do _ANO_TRIMESTRE_X)
            tipo = re.sub(r'_\d{4}_[A-Z]+_\d+\.csv$', '', f)
            print(f"  {f} -> tipo: {tipo}")
else:
    print(f"[ERRO] Pasta {pasta} não encontrada")
