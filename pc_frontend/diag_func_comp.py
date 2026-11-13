import re

with open("composicao_receitas_despesas.html", "r", encoding="utf-8") as f:
    html = f.read()

print("=== TODAS AS FUNÇÕES NO ARQUIVO ===")
for m in re.finditer(r'(async\s+)?function\s+(\w+)\s*\(', html):
    print(f"  - {m.group(2)}")

print("\n=== BOTÃO VERIFICAR ===")
for m in re.finditer(r'<button[^>]*onclick="([^"]*)"[^>]*>([^<]*)</button>', html):
    if 'Verificar' in m.group(2) or 'verificar' in m.group(1).lower():
        print(f"  Botão: {m.group(2).strip()}")
        print(f"  onclick: {m.group(1)}")

print("\n=== FUNÇÃO QUE FAZ FETCH DA API ===")
# Procura qualquer função que tenha fetch com /api/composicao
padrao = re.compile(r'function\s+(\w+)\s*\([^)]*\)\s*\{.*?fetch\([\'"]/api/composicao', re.DOTALL)
match = padrao.search(html)
if match:
    print(f"  Função: {match.group(1)}")
    # Pega o bloco completo
    inicio = match.start()
    nivel = 0
    fim = -1
    for i in range(inicio, len(html)):
        if html[i] == '{':
            nivel += 1
        elif html[i] == '}':
            nivel -= 1
            if nivel == 0:
                fim = i + 1
                break
    if fim > 0:
        print(html[inicio:fim][:800])
else:
    print("  Nenhuma função encontrada com fetch para /api/composicao")
