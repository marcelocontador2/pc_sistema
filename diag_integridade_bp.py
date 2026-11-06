c = open(r"pc_backend\integridade.py", encoding="utf-8-sig").read()

print("=" * 70)
print("1) TRECHO QUE CALCULA O BALANCO PATRIMONIAL (BP)")
print("=" * 70)
# Procura por "Balanço Patrimonial" ou "BP" ou "passivo_total"
idx = c.find('Balanço Patrimonial')
if idx == -1:
    idx = c.find('passivo_total')
if idx == -1:
    idx = c.find('ativo_total')

if idx != -1:
    # Mostra 50 linhas ao redor
    inicio = max(0, idx - 2000)
    fim = min(len(c), idx + 2000)
    print(c[inicio:fim])
else:
    print("[AVISO] Nao encontrei o trecho do BP.")
    print("Mostrando todas as ocorrencias de 'ativo' ou 'passivo':")
    for i, ln in enumerate(c.split("\n"), 1):
        if 'ativo' in ln.lower() or 'passivo' in ln.lower():
            print(f"  Linha {i}: {ln.strip()[:150]}")
