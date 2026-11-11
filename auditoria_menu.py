import re

ARQ = r"pc_frontend\index.html"
with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Procura por todas as ocorrências de "notas_explicativas" no arquivo
print("=== 1. OCORRÊNCIAS DE 'notas_explicativas' ===")
for i, linha in enumerate(html.split(chr(10))):
    if 'notas_explicativas' in linha.lower():
        print(f"Linha {i+1}: {linha.strip()[:200]}")

# 2. Procura o bloco que monta o menu principal (onde o JS pode estar removendo o link)
print("\n=== 2. CÓDIGO QUE MONTA O MENU (linksParaMover / ordemLinks) ===")
padrao = r'(const linksParaMover = \[.*?\];|const ordemLinks = \[.*?\];)'
matches = re.findall(padrao, html, re.DOTALL)
for m in matches:
    print(m[:500])
    print("...")

# 3. Procura o código que insere o menu de Análises e se ele remove o link de Notas
print("\n=== 3. INSERÇÃO DO MENU DE ANÁLISES ===")
padrao2 = r'(// 4\. Insere o menu de Análises.*?)(?=\n\s*//|\n\s*function|\n\s*document)'
match2 = re.search(padrao2, html, re.DOTALL)
if match2:
    print(match2.group(1)[:500])
else:
    print("[AVISO] Bloco de inserção não encontrado.")

# 4. Verifica se o HTML tem o link como item principal (estático)
print("\n=== 4. HTML ESTÁTICO (linha 148-150) ===")
linhas = html.split(chr(10))
for i in range(145, min(155, len(linhas))):
    print(f"Linha {i+1}: {linhas[i].strip()[:200]}")
