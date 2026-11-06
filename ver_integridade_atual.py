c = open(r"pc_backend\integridade.py", encoding="utf-8-sig").read()

# Localiza o trecho do BP
idx = c.find("BALANÇO PATRIMONIAL")
if idx == -1:
    idx = c.find("Balanço Patrimonial")
if idx == -1:
    idx = c.find("passivo")

if idx != -1:
    inicio = max(0, idx - 500)
    fim = min(len(c), idx + 1500)
    print("=" * 70)
    print("TRECHO ATUAL DO BP NO integridade.py")
    print("=" * 70)
    print(c[inicio:fim])
else:
    print("[ERRO] Trecho do BP nao encontrado.")
