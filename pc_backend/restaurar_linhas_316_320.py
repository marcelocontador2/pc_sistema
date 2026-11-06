import shutil, glob, os, ast

# Pega o backup mais recente do fix_2niveis
backups = sorted(glob.glob("main.py.bak_fix_2niveis_*"), key=os.path.getmtime)
if not backups:
    print("[ERRO] Backup do fix_2niveis nao encontrado.")
    exit(1)
bak = backups[-1]
print(f"[INFO] Restaurando de: {bak}")

c_orig = open(bak, encoding="utf-8-sig").read()
linhas_orig = c_orig.split("\n")

# Le o arquivo atual
c_atual = open("main.py", encoding="utf-8-sig").read()
linhas_atual = c_atual.split("\n")

# Restaura APENAS as linhas 316-320 (indice 315 a 319)
# (linhas 31, 107, 469, 315 sao comentarios/prints, podem ficar como estao)
for idx in range(315, 320):
    if idx < len(linhas_orig) and idx < len(linhas_atual):
        linhas_atual[idx] = linhas_orig[idx]
        print(f"[OK] Linha {idx+1} restaurada.")

c_novo = "\n".join(linhas_atual)
open("main.py", "w", encoding="utf-8").write(c_novo)

# Valida
try:
    ast.parse(open("main.py", encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(bak, "main.py")
    print("[OK] Backup completo restaurado.")
