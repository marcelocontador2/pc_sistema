c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

# Localiza o trecho do calculo do BP (procurando por "ativo_total =")
idx = c.find('ativo_total = ')
if idx == -1:
    print("[ERRO] Trecho do BP nao encontrado.")
else:
    # Pega 30 linhas antes e 10 depois
    inicio = max(0, idx - 2000)
    fim = min(len(c), idx + 1000)
    bloco = c[inicio:fim]
    
    print("=" * 70)
    print("TRECHO ATUAL DO CALCULO DO BP")
    print("=" * 70)
    print(bloco)
