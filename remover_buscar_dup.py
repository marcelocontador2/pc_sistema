import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_remove_buscar_dup_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Encontra todas as definicoes de "def buscar("
ocorrencias = [(m.start(), m.group()) for m in re.finditer(r'def buscar\([^)]+\):', c)]
print(f"[INFO] Encontradas {len(ocorrencias)} definicoes de 'buscar'.")

if len(ocorrencias) <= 1:
    print("[AVISO] So ha uma definicao de buscar. O problema pode estar em outro lugar.")
else:
    # Remove a definicao antiga (a que NAO tem "col_espec in [0, 3]")
    # Primeiro, encontra o bloco de cada uma
    for idx, match in ocorrencias:
        # Pega o bloco (ate o proximo "def" ou 1000 chars)
        fim = c.find('\n    def ', idx + 10)
        if fim == -1:
            fim = c.find('\ndef ', idx + 10)
        if fim == -1:
            fim = idx + 1000
        bloco = c[idx:fim]

        if 'col_espec in [0, 3]' not in bloco:
            # Esta e a versao antiga - remove
            print(f"[INFO] Removendo definicao antiga em: {match}")
            print(f"  Bloco: {bloco[:100]}...")
            c = c[:idx] + c[fim:]
            print("[OK] Definicao antiga removida.")
            break

open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_remove_buscar_dup_{ts}", back_path)
    print("[OK] Backup restaurado.")
