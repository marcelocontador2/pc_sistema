import csv, os

# Localiza o CSV do DMPL
pasta = r"pc_storage\uploads_raw"
arquivo = None
for f in sorted(os.listdir(pasta), reverse=True):
    if f.startswith("DMPL") and f.endswith(".csv"):
        arquivo = os.path.join(pasta, f)
        break

if not arquivo:
    print("[ERRO] Nenhum CSV de DMPL encontrado.")
    exit(1)

print(f"Analisando: {os.path.basename(arquivo)}\n")

# Lê e mostra as primeiras 20 linhas
try:
    with open(arquivo, "r", encoding="utf-8-sig") as f:
        linhas = f.readlines()
except:
    with open(arquivo, "r", encoding="latin-1") as f:
        linhas = f.readlines()

print("=== PRIMEIRAS 20 LINHAS DO CSV ===")
for i, linha in enumerate(linhas[:20]):
    print(f"[{i}] {repr(linha[:200])}")

print("\n=== PROCURANDO POR 'RESULTADO' NO CSV ===")
for i, linha in enumerate(linhas):
    if "RESULTADO" in linha.upper():
        print(f"[{i}] {repr(linha[:200])}")

print("\n=== PROCURANDO POR 'SALDOS INICIAIS' E 'SALDOS FINAIS' ===")
for i, linha in enumerate(linhas):
    if "SALDOS INICIAIS" in linha.upper() or "SALDOS FINAIS" in linha.upper():
        print(f"[{i}] {repr(linha[:200])}")
