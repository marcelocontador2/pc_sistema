import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_verif_bp_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Localiza o trecho da verificacao do BP (linha 1029)
idx = c.find("ativo_total = passivo_total + pl")
if idx == -1:
    print("[ERRO] Trecho de verificacao do BP nao encontrado.")
    exit(1)

# Pega o bloco ao redor (50 linhas antes e 20 depois)
inicio = c.rfind("def", 0, idx)
if inicio == -1:
    inicio = max(0, idx - 2000)
fim = c.find("def", idx + 100)
if fim == -1:
    fim = min(len(c), idx + 2000)

bloco = c[inicio:fim]
print("=" * 70)
print("TRECHO ATUAL DA VERIFICACAO DO BP")
print("=" * 70)
print(bloco)
