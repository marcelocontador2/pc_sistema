import re

with open("analise_orcamentaria.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=" * 70)
print("ANÁLISE ORÇAMENTÁRIA (BO) - O QUE FUNCIONA")
print("=" * 70)

print("\n[1] BOTÃO EXIBIR:")
for m in re.finditer(r'<button[^>]*>([^<]*Exibir[^<]*)</button>', s, re.IGNORECASE):
    print(m.group(0))

print("\n[2] FUNÇÃO exibirSelecionado (ou similar):")
padrao = re.compile(r'(async\s+)?function\s+(\w*exibir\w*|exibir\w*)\s*\([^)]*\)\s*\{.*?(?=\n\s*function|\Z)', re.DOTALL | re.IGNORECASE)
for m in re.finditer(r'(async\s+)?function\s+(\w+)\s*\([^)]*\)\s*\{', s):
    nome = m.group(2)
    if 'exibir' in nome.lower() or 'historico' in nome.lower():
        print(f"Função encontrada: {nome}")
        # Pega o bloco
        inicio = m.start()
        nivel = 0
        fim = -1
        for i in range(inicio, len(s)):
            if s[i] == '{':
                nivel += 1
            elif s[i] == '}':
                nivel -= 1
                if nivel == 0:
                    fim = i + 1
                    break
        if fim > 0:
            print(s[inicio:fim][:2000])

print("\n[3] IDs DAS TABELAS:")
for m in re.finditer(r'<table[^>]*id="([^"]+)"', s):
    print(f"  - {m.group(1)}")

print("\n[4] ROTAS FETCH:")
for m in re.finditer(r'fetch\(\s*[`\'"]([^`\'"]+)', s):
    print(f"  - {m.group(1)}")
