import re

c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()

print("=" * 70)
print("1) SCRIPTS QUE MANIPULAM O SUBMENU (submenuAnalises)")
print("=" * 70)
# Encontra todos os blocos de script que contenham "submenuAnalises"
for m in re.finditer(r'<script>(.*?)</script>', c, re.DOTALL):
    bloco = m.group(1)
    if 'submenuAnalises' in bloco or 'linksParaMover' in bloco or 'setTimeout' in bloco:
        print(f"--- Script encontrado (tamanho {len(bloco)} chars) ---")
        # Mostra apenas as primeiras linhas
        for i, ln in enumerate(bloco.split("\n")[:15]):
            print(f"  {ln.strip()[:120]}")
        print()

print("\n" + "=" * 70)
print("2) OCORRENCIAS DE 'setTimeout' NO ARQUIVO")
print("=" * 70)
for i, ln in enumerate(c.split("\n"), 1):
    if 'setTimeout' in ln:
        print(f"  Linha {i}: {ln.strip()[:150]}")

print("\n" + "=" * 70)
print("3) OCORRENCIAS DE 'submenuAnalises' NO ARQUIVO")
print("=" * 70)
for i, ln in enumerate(c.split("\n"), 1):
    if 'submenuAnalises' in ln:
        print(f"  Linha {i}: {ln.strip()[:150]}")
