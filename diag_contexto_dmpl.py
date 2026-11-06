import re

c = open(r"pc_backend\main.py", encoding='utf-8-sig').read()

print("=" * 70)
print("1) TRECHO DO CÓDIGO ONDE 'content' É DEFINIDO")
print("=" * 70)
for i, ln in enumerate(c.split('\n'), 1):
    if re.search(r'content\s*=', ln) and 'splitlines' not in ln:
        print(f"  Linha {i}: {ln.strip()[:200]}")

print("\n" + "=" * 70)
print("2) LINHAS 515-545 DO ARQUIVO (contexto da função e layout)")
print("=" * 70)
linhas = c.split('\n')
for i in range(514, min(546, len(linhas))):
    print(f"  {i+1}: {linhas[i]}")

print("\n" + "=" * 70)
print("3) TODAS AS OCORRÊNCIAS DE 'Resultado' (case-insensitive)")
print("=" * 70)
for i, ln in enumerate(c.split('\n'), 1):
    if 'resultado' in ln.lower():
        print(f"  Linha {i}: {ln.strip()[:200]}")
