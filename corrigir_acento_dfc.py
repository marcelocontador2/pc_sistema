import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = "pc_backend/app/routers/dfc.py"
shutil.copy2(back_path, f"{back_path}.bak_acento_{ts}")

c = open(back_path, encoding="utf-8", errors="ignore").read()

# Substitui a busca com acento por prefixo sem acento
c = c.replace('"FLUXO DE CAIXA LÍQUIDO"', '"FLUXO DE CAIXA L"')
c = c.replace('"FLUXO DE CAIXA LÃQUIDO"', '"FLUXO DE CAIXA L"')

# Também corrige a busca da geração (sem acento)
c = c.replace('"GERA"', '"GERA"')  # já está sem acento, ok

open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Busca por 'FLUXO DE CAIXA L' (sem acento) aplicada e sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_acento_{ts}", back_path)
