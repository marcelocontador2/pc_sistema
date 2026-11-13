import re

with open("analise_dmpl.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. FUNCAO verificarDados (ou similar) ===")
# Procura funcoes com 'verificar' ou 'verificarDados' ou 'carregar'
funcoes = re.findall(r'function\s+(verificarDados|carregarDados|verificar|carregar)\s*\([^)]*\)\s*\{.*?(?=\n\s*function|\Z)', s, re.DOTALL)
if not funcoes:
    print("Nenhuma funcao de verificacao encontrada.")
else:
    for f in funcoes:
        print(f"\n--- Funcao encontrada ---")
        print(f[:2000])

print("\n=== 2. BOTOES NA PAGINA ===")
botoes = re.findall(r'<button[^>]*>([^<]*)</button>', s)
for b in botoes:
    if 'Verificar' in b or 'verificar' in b:
        match = re.search(r'<button[^>]*>' + re.escape(b) + r'</button>', s)
        if match:
            print(f"  {match.group(0)}")
