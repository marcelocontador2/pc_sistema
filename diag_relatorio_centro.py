import re

c = open(r"pc_frontend\relatorio_centro_custos_v2.html", encoding="utf-8-sig").read()

print("=" * 70)
print("DIAGNÓSTICO: COMO O RELATÓRIO V2 BUSCA OS DADOS")
print("=" * 70)

# 1. Procura chamadas fetch
print("\n--- CHAMADAS FETCH ---")
for m in re.finditer(r'fetch\(([^)]+)\)', c):
    print(f"  {m.group(0)[:150]}")

# 2. Procura como os dados são renderizados (funções)
print("\n--- FUNÇÕES JAVASCRIPT ---")
for m in re.finditer(r'function\s+([a-zA-Z0-9_]+)\s*\(', c):
    print(f"  {m.group(1)}")

# 3. Procura onde ele lê o historico_id ou periodo
print("\n--- COMO ELE LÊ OS PARÂMETROS DA URL ---")
if "URLSearchParams" in c:
    print("  Usa URLSearchParams (bom sinal)")
else:
    print("  NÃO usa URLSearchParams!")

# 4. Mostra o bloco do DOMContentLoaded ou inicialização principal
print("\n--- BLOCO DE INICIALIZAÇÃO ---")
match = re.search(r'(document\.addEventListener\(\'DOMContentLoaded\'.*?\}\);)', c, re.DOTALL)
if match:
    print(match.group(1)[:800])
else:
    # Tenta achar algo como window.onload
    match = re.search(r'(window\.onload\s*=\s*function.*?\})', c, re.DOTALL)
    if match:
        print(match.group(1)[:800])
    else:
        print("Não encontrei o bloco de inicialização explícito.")

# 5. Mostra o começo do script onde ele processa as variáveis do fetch
print("\n--- TRECHO ONDE O FETCH É PROCESSADO (.then) ---")
match = re.search(r'\.then\([^)]*=>\s*\{.*?\}\)', c, re.DOTALL)
if match:
    print(match.group(0)[:800])
