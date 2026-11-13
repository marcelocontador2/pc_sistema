import re

caminho = "pc_frontend/analise_comparativo_despesas.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

print("=" * 70)
print("AUDITORIA DEFINITIVA - HTML DE DESPESAS")
print("=" * 70)

print(f"Tamanho do arquivo: {len(html)} caracteres")

# 1. Verifica se o HTML tem as tags básicas
print("\n1. Tags básicas:")
for tag in ['<html', '</html>', '<body', '</body>', '<script>', '</script>']:
    print(f"   {tag}: {'✅' if tag in html else '❌'}")

# 2. Verifica se os containers existem
print("\n2. Containers:")
for id_ in ['tabela-container', 'card-realizado', 'card-orcado', 'card-percentual', 'historico-lista']:
    print(f"   id='{id_}': {'✅' if f'id=\"{id_}\"' in html else '❌'}")

# 3. Verifica as funções
print("\n3. Funções JavaScript:")
for f in ['verificar', 'exibirSelecionado', 'carregarHistorico', 'renderizarTabela', 'atualizarCards']:
    print(f"   function {f}: {'✅' if f'function {f}(' in html else '❌'}")

# 4. Mostra a estrutura de divs (para ver se está balanceada)
print("\n4. Estrutura de divs:")
abre_div = len(re.findall(r'<div\b', html))
fecha_div = len(re.findall(r'</div>', html))
print(f"   <div>: {abre_div} abertas, </div>: {fecha_div} fechadas {'✅' if abre_div == fecha_div else '❌ DESBALANCEADO'}")

# 5. Mostra o trecho do body (primeiros 2000 caracteres)
print("\n5. Trecho do <body> (primeiros 2000 chars):")
idx_body = html.find('<body')
print(html[idx_body:idx_body+2000] if idx_body != -1 else "❌ <body> não encontrado")

# 6. Mostra o bloco <script> (primeiros 1000 caracteres)
print("\n6. Bloco <script> (primeiros 1000 chars):")
idx_script = html.find('<script>')
if idx_script != -1:
    print(html[idx_script:idx_script+1000])
else:
    print("❌ <script> não encontrado")
