import re

with open("analise_dmpl.html", "r", encoding="utf-8") as f:
    s = f.read()

# Extrai o JS
blocos = re.findall(r'<script>(.*?)</script>', s, re.DOTALL)
js = "\n".join(blocos)

linhas = js.split('\n')
saldo = 0
print("=== LINHAS COM DESBALANCEAMENTO ===")
for i, linha in enumerate(linhas, 1):
    a = linha.count('{')
    f = linha.count('}')
    if a != f:
        print(f"Linha {i}: abertura={a} fechamento={f} -> {linha.strip()[:80]}")
    saldo += a - f

print(f"\nSaldo total de chaves: {saldo}")
if saldo != 0:
    print(f"Faltam {abs(saldo)} chaves de {'fechamento' if saldo > 0 else 'abertura'}.")
