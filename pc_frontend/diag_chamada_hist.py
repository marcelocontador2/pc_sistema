import re

with open("conferencia.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. ROTAS FETCH NA FUNCAO carregarHistorico ===")
# Pega o bloco da funcao carregarHistorico
match = re.search(r'function carregarHistorico\(\)\s*\{.*?(?=\n\s*function|\Z)', s, re.DOTALL)
if match:
    bloco = match.group(0)
    # Procura fetch dentro do bloco
    fetches = re.findall(r'fetch\(\s*[`\'"]([^`\'"]+)', bloco)
    for f_url in fetches:
        print(f"  - {f_url}")
else:
    print("  Funcao nao encontrada.")

print("\n=== 2. COMO A FUNCAO E CHAMADA ===")
# Procura por carregarHistorico() sendo chamada
chamadas = re.findall(r'(DOMContentLoaded|onload|init|carregarHistorico)\s*[=\(]', s)
print(f"  Ocorrencias de inicializacao: {set(chamadas)}")

# Ve se tem carregarHistorico() solto no final
if 'carregarHistorico();' in s:
    print("  Chamada direta 'carregarHistorico();' encontrada no arquivo.")

print("\n=== 3. TRECHO DO DOMContentLoaded ===")
# Acha o DOMContentLoaded e mostra 500 caracteres depois
for m in re.finditer(r'DOMContentLoaded', s):
    inicio = max(0, m.start() - 100)
    fim = min(len(s), m.start() + 500)
    print(s[inicio:fim])
    print("-" * 50)
