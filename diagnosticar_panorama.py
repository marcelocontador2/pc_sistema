import re

arquivo = "pc_frontend/panorama.html"
with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

print("=== ANALISE DO ARQUIVO PANORAMA.HTML ===\n")

# 1. Procura as chamadas de funcao nos botoes (onclick)
print("1) Botoes e chamadas onclick:")
for m in re.finditer(r'<button[^>]*onclick=["\']([^"\']+)["\'][^>]*>(.*?)</button>', html, re.IGNORECASE | re.DOTALL):
    onclick = m.group(1)
    texto = re.sub(r'<[^>]+>', '', m.group(2)).strip()
    print(f"   Botao: '{texto}' -> {onclick}")

# 2. Procura as definicoes de funcao no JS
print("\n2) Funcoes encontradas no JavaScript:")
for m in re.finditer(r'function\s+([a-zA-Z0-9_]+)\s*\(', html):
    print(f"   function {m.group(1)}()")

# 3. Checa se tem erro grosseiro (tags script abertas e fechadas)
print("\n3) Contagem de tags <script>:")
print(f"   Aberturas: {html.lower().count('<script')}")
print(f"   Fechamentos: {html.lower().count('</script>')}")

# 4. Tenta extrair o script principal (o maior bloco)
print("\n4) Ultimas 40 linhas do ultimo bloco <script> (para ver se nao truncou):")
scripts = re.findall(r'<script.*?>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
if scripts:
    ultimo_script = scripts[-1]
    linhas = ultimo_script.strip().split('\n')
    for linha in linhas[-40:]:
        print("   " + linha)
else:
    print("   (Nenhum script encontrado)")
