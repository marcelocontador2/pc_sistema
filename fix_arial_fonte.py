import os, shutil, datetime, re, ast

print("=" * 70)
print("DIAGNÓSTICO: FONTE DEJAVU NO WINDOWS")
print("=" * 70)

# 1. Verifica se DejaVu existe no Windows
fontes_windows = [
    r"C:\Windows\Fonts\DejaVuSans.ttf",
    r"C:\Windows\Fonts\DejaVuSans-Bold.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
]

print("\n--- FONTES NO WINDOWS ---")
for f in fontes_windows:
    print(f"  {f}: {'EXISTE' if os.path.exists(f) else 'NAO EXISTE'}")

# 2. Verifica se já tem alguma fonte na pasta backend
print("\n--- FONTES NA PASTA BACKEND ---")
pasta_backend = r"pc_backend"
fontes_ttf = [f for f in os.listdir(pasta_backend) if f.endswith('.ttf')]
if fontes_ttf:
    for f in fontes_ttf:
        print(f"  {f}: {os.path.getsize(os.path.join(pasta_backend, f))} bytes")
else:
    print("  Nenhuma fonte .ttf na pasta backend")

# 3. Copia a Arial (sempre existe no Windows) para o backend
print("\n--- COPIANDO FONTE ARIA ---")
arial = r"C:\Windows\Fonts\arial.ttf"
arial_bold = r"C:\Windows\Fonts\arialbd.ttf"

if os.path.exists(arial):
    shutil.copy2(arial, os.path.join(pasta_backend, "arial.ttf"))
    print(f"  [OK] arial.ttf copiada")
else:
    print(f"  [ERRO] arial.ttf nao encontrada")

if os.path.exists(arial_bold):
    shutil.copy2(arial_bold, os.path.join(pasta_backend, "arialbd.ttf"))
    print(f"  [OK] arialbd.ttf copiada")

# 4. Corrige o main.py para usar Arial em vez de DejaVu
print("\n--- CORRIGINDO main.py ---")
back_path = r"pc_backend\main.py"
ts = datetime.datetime.now().strftime('%H%M%S')
shutil.copy2(back_path, f"{back_path}.bak_arial_{ts}")

c = open(back_path, encoding='utf-8-sig').read()

# Substitui DejaVu por Arial nos caminhos
c = c.replace('DejaVuSans.ttf', 'arial.ttf')
c = c.replace('DejaVuSans-Bold.ttf', 'arialbd.ttf')
c = c.replace('"DejaVu"', '"ArialUnicode"')

# Adiciona um fallback: se a fonte não for encontrada, usa Helvetica mas limpa os caracteres
c = c.replace(
    'fonte_padrao = "Helvetica"',
    'fonte_padrao = "Helvetica"'
)

# Garante que _limpar_ascii seja aplicada se a fonte não for encontrada
# (A função _limpar_pdf mantém acentos, mas se a fonte for Helvetica, os acentos podem falhar)
# Vou adicionar uma verificação: se fonte_padrao == "Helvetica", usa _limpar_ascii

# Substitui _limpar_pdf por uma função que decide baseado na fonte
c = c.replace(
    '_limpar_pdf(h)',
    '(_limpar_pdf(h) if fonte_padrao != "Helvetica" else _limpar_ascii(h))'
)
c = c.replace(
    '_limpar_pdf(txt)',
    '(_limpar_pdf(txt) if fonte_padrao != "Helvetica" else _limpar_ascii(txt))'
)
c = c.replace(
    '_limpar_pdf(titulo_pdf)',
    '(_limpar_pdf(titulo_pdf) if fonte_padrao != "Helvetica" else _limpar_ascii(titulo_pdf))'
)
c = c.replace(
    '_limpar_pdf(f"Periodo: {periodo_formatado}")',
    '(_limpar_pdf(f"Periodo: {periodo_formatado}") if fonte_padrao != "Helvetica" else _limpar_ascii(f"Periodo: {periodo_formatado}"))'
)

open(back_path, 'w', encoding='utf-8').write(c)

# Valida sintaxe
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_arial_{ts}", back_path)
    print("[OK] Backup restaurado")
