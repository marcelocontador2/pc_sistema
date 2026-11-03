import re

c = open(r"pc_frontend\panorama.html", encoding="utf-8-sig").read()

print("=" * 70)
print("DIAGNÓSTICO COMPLETO DO PANORAMA.HTML")
print("=" * 70)

# 1. Funções de fetch encontradas
print("\n--- CHAMADAS FETCH ENCONTRADAS ---")
for m in re.finditer(r'fetch\([^)]+\)', c):
    print(f"  {m.group(0)[:120]}")

# 2. Como o histórico é exibido
print("\n--- TRECHO DO HISTÓRICO ---")
match_hist = re.search(r'.{0,200}(historico|Histórico).{0,300}', c, re.IGNORECASE)
if match_hist:
    print(match_hist.group(0).strip()[:500])

# 3. Como o botão de PDF está configurado
print("\n--- BOTÃO DE PDF ---")
match_pdf = re.search(r'.{0,150}(pdf|PDF|gerar_pdf).{0,150}', c)
if match_pdf:
    print(match_pdf.group(0).strip()[:300])

# 4. Verifica se existe alguma função de renderizar o panorama
print("\n--- FUNÇÕES JAVASCRIPT DEFINIDAS ---")
for m in re.finditer(r'function\s+([a-zA-Z0-9_]+)\s*\(', c):
    print(f"  - {m.group(1)}")
