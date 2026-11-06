import re

with open(r"pc_backend\main.py", "r", encoding="utf-8") as f:
    codigo = f.read()

print("=" * 70)
print("AUDITORIA DE FONTES NO main.py")
print("=" * 70)

# 1. Encontra todas as chamadas set_font("Helvetica", ...)
print("\n[1] CHAMADAS set_font(\"Helvetica\", ...) NO CÓDIGO")
print("-" * 70)
for m in re.finditer(r'set_font\(\s*"Helvetica"\s*,[^)]+\)', codigo):
    linha = codigo[:m.start()].count("\n") + 1
    print(f"  Linha {linha}: {m.group(0)}")

# 2. Encontra todas as chamadas set_font(fonte_padrao, ...)
print("\n[2] CHAMADAS set_font(fonte_padrao, ...)")
print("-" * 70)
for m in re.finditer(r'set_font\(\s*fonte_padrao\s*,[^)]+\)', codigo):
    linha = codigo[:m.start()].count("\n") + 1
    print(f"  Linha {linha}: {m.group(0)}")

# 3. Encontra todas as definições de fonte_padrao
print("\n[3] DEFINIÇÕES DE fonte_padrao")
print("-" * 70)
for m in re.finditer(r'fonte_padrao\s*=\s*["\'][^"\']+["\']', codigo):
    linha = codigo[:m.start()].count("\n") + 1
    print(f"  Linha {linha}: {m.group(0)}")

# 4. Encontra todas as chamadas add_font (para ver se alguma foi injetada)
print("\n[4] CHAMADAS add_font NO CÓDIGO")
print("-" * 70)
for m in re.finditer(r'add_font\([^)]+\)', codigo):
    linha = codigo[:m.start()].count("\n") + 1
    print(f"  Linha {linha}: {m.group(0)[:100]}")

# 5. Encontra o monkey-patch (se foi injetado)
print("\n[5] MONKEY-PATCH DO FPDF")
print("-" * 70)
if "MONKEY-PATCH PARA UTF-8" in codigo:
    idx = codigo.find("MONKEY-PATCH PARA UTF-8")
    print(f"  Encontrado na linha {codigo[:idx].count(chr(10)) + 1}")
    print(f"  Trecho: {codigo[idx:idx+300]}...")
else:
    print("  NÃO ENCONTRADO")

# 6. Encontra a criação do app
print("\n[6] CRIAÇÃO DO APP")
print("-" * 70)
for m in re.finditer(r'^app\s*=\s*FastAPI\s*\(', codigo, re.MULTILINE):
    linha = codigo[:m.start()].count("\n") + 1
    print(f"  Linha {linha}: {m.group(0)}")
