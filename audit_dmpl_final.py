import ast

caminho = "pc_backend/main.py"
with open(caminho, "r", encoding="utf-8") as f:
    conteudo = f.read()

print("=== 1. DMPL NOS DICIONARIOS DA API ===")
if '"dmpl": "historico_analise_dmpl"' in conteudo:
    print("✅ 'dmpl' esta no dicionario 'modulos'.")
else:
    print("❌ 'dmpl' NAO esta no dicionario 'modulos'.")

if '"dmpl": "Demonstração das Mutações do PL (DMPL)"' in conteudo:
    print("✅ 'dmpl' esta no dicionario 'nomes_amigaveis'.")
else:
    print("❌ 'dmpl' NAO esta no dicionario 'nomes_amigaveis'.")

print("\n=== 2. BLOCO DO ITEM 7 (elif nome_interno == 'DMPL') ===")
idx = conteudo.find('elif nome_interno == "DMPL":')
if idx != -1:
    print("✅ Bloco do item 7 encontrado.")
    trecho = conteudo[idx:idx+300]
    print("Trecho inicial:")
    print(trecho)
else:
    print("❌ Bloco do item 7 NAO encontrado.")

print("\n=== 3. SINTAXE DO main.py ===")
try:
    ast.parse(conteudo)
    print("✅ Sintaxe OK.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
