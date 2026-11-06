import os, re

print("=" * 70)
print("DIAGNÓSTICO: FONTE E LIMPEZA")
print("=" * 70)

# 1. Verifica se arial.ttf existe
arial_path = r"pc_backend\arial.ttf"
print(f"\n--- 1. FONTE ARIA ---")
print(f"arial.ttf: {'EXISTE' if os.path.exists(arial_path) else 'NAO EXISTE'}")
if os.path.exists(arial_path):
    print(f"  Tamanho: {os.path.getsize(arial_path)} bytes")

# 2. Verifica se o main.py tem o bloco de registro da fonte
c = open(r"pc_backend\main.py", encoding='utf-8-sig').read()

print(f"\n--- 2. REGISTRO DA FONTE NO main.py ---")
if 'pdf.add_font' in c:
    idx = c.find('pdf.add_font')
    print(c[max(0,idx-500):idx+500])
else:
    print("  [AVISO] Nenhum 'pdf.add_font' encontrado")

# 3. Verifica se _limpar_ascii está sendo usada nas células
print(f"\n--- 3. _LIMPAR_ASCII NAS CÉLULAS ---")
# Procura as chamadas de pdf.multi_cell e pdf.cell com _limpar_ascii
for m in re.finditer(r'pdf\.(cell|multi_cell)\([^)]*_limpar_ascii[^)]*\)', c):
    print(f"  {m.group(0)[:120]}")

# 4. Verifica se _limpar_pdf está sendo usada nas células
print(f"\n--- 4. _LIMPAR_PDF NAS CÉLULAS ---")
for m in re.finditer(r'pdf\.(cell|multi_cell)\([^)]*_limpar_pdf[^)]*\)', c):
    print(f"  {m.group(0)[:120]}")

# 5. Verifica se há chamadas SEM limpeza (suspeitas)
print(f"\n--- 5. CHAMADAS DE pdf.cell/multi_cell SEM LIMPEZA (SUSPEITAS) ---")
for i, ln in enumerate(c.split('\n'), 1):
    if ('pdf.cell(' in ln or 'pdf.multi_cell(' in ln) and '_limpar' not in ln and 'border' in ln:
        print(f"  Linha {i}: {ln.strip()[:120]}")

# 6. Verifica o que a _limpar_ascii faz com \f
print(f"\n--- 6. TESTE DA _LIMPAR_ASCII COM \\f ---")
# Simula a função
def _limpar_ascii(txt):
    if not txt: return ""
    s = str(txt)
    s = s.replace("\t", " ").replace("\n", " ").replace("\r", " ")
    s = s.replace("\f", " ").replace("\v", " ").replace("\a", " ")
    s = s.replace(chr(12), " ").replace(chr(11), " ").replace(chr(7), " ")
    s = "".join(ch if 32 <= ord(ch) <= 126 else " " for ch in s)
    return s

teste = "Balanço\fFinanceiro"
print(f"  Entrada: {repr(teste)}")
print(f"  Saída:   {repr(_limpar_ascii(teste))}")
