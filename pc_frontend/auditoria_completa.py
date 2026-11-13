import re

with open("analise_patrimonial.html", "r", encoding="utf-8") as f:
    s = f.read()

blocos = re.findall(r'<script>(.*?)</script>', s, re.DOTALL)
js = "\n".join(blocos)

print("=== AUDITORIA DE SINTAXE ===")
print(f"Chaves abertas: {js.count('{')} | fechadas: {js.count('}')}")
print(f"Parenteses abertas: {js.count('(')} | fechadas: {js.count(')')}")

if js.count('{') != js.count('}'):
    print("❌ ERRO: Chaves desbalanceadas no JavaScript!")
if js.count('(') != js.count(')'):
    print("❌ ERRO: Parenteses desbalanceados no JavaScript!")
if js.count('{') == js.count('}') and js.count('(') == js.count(')'):
    print("✅ Sintaxe do JavaScript esta balanceada.")

print("\n=== FUNCAO exibirSelecionado ===")
padrao = re.compile(r'function exibirSelecionado\s*\([^)]*\)\s*\{.*?\n\s*\}', re.DOTALL)
match = padrao.search(js)
if match:
    print(match.group(0))
else:
    print("❌ Funcao exibirSelecionado NAO encontrada no JS.")

print("\n=== BOTOES (onclick) ===")
for m in re.finditer(r'<button[^>]*onclick="([^"]*)"[^>]*>([^<]*)</button>', s):
    print(f"Botao '{m.group(2).strip()}' -> {m.group(1)}")

print("\n=== FUNCAO DE RENDERIZACAO ===")
if 'function desenharTela' in js:
    print("✅ Funcao desenharTela existe no JS.")
else:
    print("❌ Funcao desenharTela NAO existe no JS.")

print("\n=== FUNCAO gerarPDF ===")
if 'function gerarPDF' in js:
    print("✅ Funcao gerarPDF existe no JS.")
else:
    print("❌ Funcao gerarPDF NAO existe no JS.")

print("\n=== CHECKBOX CLASS ===")
m = re.search(r'class="([^"]*check[^"]*)"', s)
if m:
    print(f"Classe do checkbox encontrada: {m.group(1)}")
else:
    print("❌ Checkbox nao encontrado no HTML.")
