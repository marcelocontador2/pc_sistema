import re, shutil, datetime

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_latin1_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    codigo = f.read()

# 1. Encontra todas as ocorrências de encoding="utf-8" que abrem CSV
# Substitui SOMENTE aquelas em contextos de leitura de CSV (open(...csv..., encoding="utf-8"))
padrao_csv_utf8 = re.compile(
    r'open\(([^,]+\.csv[^,]*),\s*([\'"])utf-8\2',
    re.IGNORECASE
)
matches = list(padrao_csv_utf8.finditer(codigo))
print(f"[INFO] Encontrados {len(matches)} arquivos CSV sendo abertos como utf-8.")

for m in matches:
    caminho_csv = m.group(1)
    linha = codigo[:m.start()].count("\n") + 1
    print(f"  Linha {linha}: open({caminho_csv[:60]}..., encoding='utf-8')")

# Substitui por latin-1
codigo_novo = padrao_csv_utf8.sub(
    lambda m: f'open({m.group(1)}, encoding="latin-1"',
    codigo
)

# 2. Valida e salva
try:
    compile(codigo_novo, arq_main, "exec")
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO SINTAXE] linha {e.lineno}: {e.msg}")
    exit()

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(codigo_novo)
print("[OK] main.py atualizado: todos os CSVs agora são lidos como latin-1.")
