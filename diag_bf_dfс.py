c = open("pc_backend/main.py", encoding="utf-8-sig").read()
linhas = c.split("\n")

print("=" * 70)
print("ROTAS RELACIONADAS A 'BF' (Balanco Financeiro)")
print("=" * 70)
for i, ln in enumerate(linhas, 1):
    if '@app' in ln and ('bf' in ln.lower() or 'balanco_financeiro' in ln.lower()):
        print(f"Linha {i}: {ln.strip()}")

print("\n" + "=" * 70)
print("FUNCOES RELACIONADAS A 'BF'")
print("=" * 70)
for i, ln in enumerate(linhas, 1):
    if 'def ' in ln and ('bf' in ln.lower() or 'balanco_financeiro' in ln.lower() or 'analise_financeira' in ln.lower()):
        print(f"Linha {i}: {ln.strip()}")

print("\n" + "=" * 70)
print("ARQUIVOS HTML DE ANALISE BF E DFC")
print("=" * 70)
import glob, os
for f in glob.glob("pc_frontend/*analise*"):
    print(f"  {f}")
for f in glob.glob("pc_frontend/*bf*"):
    print(f"  {f}")
for f in glob.glob("pc_frontend/*dfc*"):
    print(f"  {f}")
