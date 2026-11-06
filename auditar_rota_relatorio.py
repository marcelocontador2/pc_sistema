import re, os

print("=" * 70)
print("AUDITORIA: ROTA QUE SERVE O RELATÓRIO")
print("=" * 70)

c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

# 1. Procura rotas que sirvam o relatório
print("\n--- 1. TODAS AS ROTAS QUE MENCIONAM 'relatorio_comparativo_receitas' ---")

matches = re.finditer(r'@app\.(?:get|post)\(["\']([^"\']*relatorio_comparativo_receitas[^"\']*)["\']\)\s*\n(?:async\s+)?def\s+(\w+)\([^)]*\):', c)
encontrou = False
for m in matches:
    rota = m.group(1)
    funcao = m.group(2)
    print(f"\n  Rota: {rota}")
    print(f"  Função: {funcao}")
    
    # Mostra o corpo
    inicio = m.end()
    prox = re.search(r'\n@app\.', c[inicio:])
    fim = inicio + prox.start() if prox else len(c)
    corpo = c[inicio:fim].strip()
    print(f"  Corpo (primeiras 15 linhas):")
    for ln in corpo.split('\n')[:15]:
        print(f"    {ln}")
    encontrou = True

if not encontrou:
    print("  [AVISO] Nenhuma rota encontrada com 'relatorio_comparativo_receitas'")

# 2. Procura por FileResponse (rotas que servem HTML)
print("\n--- 2. ROTAS QUE USAM FileResponse PARA receitas ---")
file_response_matches = re.finditer(r'@app\.(?:get|post)\(["\']([^"\']*)["\']\)\s*\n(?:async\s+)?def\s+(\w+)\([^)]*\):\s*\n(?:(?!\n@app\.).)*?FileResponse', c, re.DOTALL)
for m in file_response_matches:
    rota = m.group(1)
    funcao = m.group(2)
    if "receita" in rota.lower() or "receita" in funcao.lower():
        print(f"  {rota} -> {funcao}()")

# 3. Verifica se há redirecionamento ou fallback
print("\n--- 3. VERIFICANDO SE EXISTE FALLBACK NA ROTA ---")
if "relatorio_comparativo_receitas_v2" in c:
    # Mostra 3 linhas ao redor da menção
    for i, linha in enumerate(c.split('\n'), 1):
        if "relatorio_comparativo_receitas_v2" in linha:
            print(f"  Linha {i}: {linha.strip()[:150]}")

print("\n" + "=" * 70)
print("ARQUIVOS NA PASTA (verificando tamanhos e datas)")
print("=" * 70)

pasta = r"pc_frontend"
arquivos_receitas = [f for f in os.listdir(pasta) if "receita" in f.lower() and f.endswith(".html")]

import datetime
for f in arquivos_receitas:
    caminho = os.path.join(pasta, f)
    tamanho = os.path.getsize(caminho)
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(caminho))
    print(f"  {f}")
    print(f"     Tamanho: {tamanho:,} bytes | Modificado: {mtime.strftime('%d/%m/%Y %H:%M:%S')}")

print("\n" + "=" * 70)
print("DIAGNÓSTICO")
print("=" * 70)
print("Se o arquivo 'relatorio_comparativo_receitas_v2.html' não aparece na lista,")
print("significa que o backend está servindo o arquivo 'relatorio_comparativo_receitas.html'")
print("(sem _v2) e as alterações no _v2 não chegam ao Playwright.")
