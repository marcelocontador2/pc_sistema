import re

c = open(r"pc_frontend\relatorio_centro_custos_v2.html", encoding="utf-8-sig").read()

print("=" * 70)
print("COMO O RELATÓRIO LÊ O PERÍODO DA URL")
print("=" * 70)

# Procura por URLSearchParams
match = re.search(r'const\s+\w+\s*=\s*new URLSearchParams.*?;', c, re.DOTALL)
if match:
    print(match.group(0))

# Procura por periodoAtual
match2 = re.search(r'periodoAtual\s*=\s*[^;]+;', c)
if match2:
    print(match2.group(0))

# Mostra as primeiras 50 linhas do bloco de script
print("\n--- INÍCIO DO SCRIPT ---")
match3 = re.search(r'<script>(.*?)</script>', c, re.DOTALL)
if match3:
    linhas = match3.group(1).strip().split('\n')
    for ln in linhas[:30]:
        print(ln)

# Procura onde ele monta a URL da API
print("\n--- MONTAGEM DA URL DA API ---")
match4 = re.search(r'(const\s+url\s*=\s*[^;]+;)', c)
if match4:
    print(match4.group(1))
