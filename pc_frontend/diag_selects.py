import re

with open("composicao_receitas_despesas.html", "r", encoding="utf-8") as f:
    html = f.read()

print("=== OPÇÕES DOS SELECTS NO HTML ===")
# Procura os selects e suas opções
for m in re.finditer(r'<select[^>]*id="([^"]+)"[^>]*>(.*?)</select>', html, re.DOTALL):
    select_id = m.group(1)
    opcoes = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>(.*?)</option>', m.group(2), re.DOTALL)
    print(f"\nSelect ID: '{select_id}'")
    for val, txt in opcoes:
        print(f"  - value='{val}' -> {txt.strip()}")

print("\n=== FUNÇÃO DE CARREGAR DADOS (Verificar) ===")
# Procura a função que monta a URL
padrao = re.compile(r'(async\s+)?function\s+(\w+)\s*\(\)\s*\{.*?fetch\([\'"]([^\'"]+)', re.DOTALL)
for m in re.finditer(r'async\s+function\s+(\w+)\s*\(\)\s*\{.*?fetch\([\'"]([^\'"]+)', html, re.DOTALL):
    print(f"Função: {m.group(1)}")
    print(f"  -> fetch: {m.group(2)}")
    print("  -> Código completo:")
    # Pega o bloco todo da função
    inicio = m.start()
    # Encontra o fechamento da função
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
    break
