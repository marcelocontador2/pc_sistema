import re

with open("analise_dmpl.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. FUNCAO exibirSelecionado (COMO ESTA NO ARQUIVO AGORA) ===")
match = re.search(r'function\s+exibirSelecionado\(\)\s*\{.*?(?=\n\s*function|\Z)', s, re.DOTALL)
if match:
    bloco = match.group(0)
    print(bloco[:1500])
    print("\n--- Verificando se tem 'async' no inicio ---")
    if "async function exibirSelecionado" in bloco:
        print("OK: A funcao tem 'async'!")
    else:
        print("ERRO: A funcao NAO tem 'async'! O navegador vai travar por causa do 'await'.")
else:
    print("Funcao exibirSelecionado NAO encontrada! O script pode ter sido apagado.")

print("\n=== 2. CHAMADA DO BOTAO EXIBIR NO HTML ===")
# Procura o botao que chama exibirSelecionado
btn = re.search(r'<button[^>]*onclick="exibirSelecionado\(\)"[^>]*>.*?</button>', s)
if btn:
    print(btn.group(0))
else:
    print("Botao com onclick='exibirSelecionado()' NAO encontrado!")
