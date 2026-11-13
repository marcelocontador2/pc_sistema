import re

caminho_html = "pc_frontend/relatorio_consolidado.html"
print("🔍 DIAGNÓSTICO CIRÚRGICO DO BOTÃO 'Confirmar e Salvar'\n")

with open(caminho_html, "r", encoding="utf-8") as f:
    html = f.read()
    linhas = html.split("\n")

# 1. Verifica se a função salvarRelatorioConsolidado está definida no escopo global
print("1. VERIFICANDO O ESCOPO DA FUNÇÃO:")
if "async function salvarRelatorioConsolidado" in html:
    print("   ✅ A função 'async function salvarRelatorioConsolidado' está no HTML.")
    
    # Verifica se está antes ou depois do botão
    idx_func = html.find("async function salvarRelatorioConsolidado")
    idx_btn = html.find('onclick="salvarRelatorioConsolidado()"')
    
    if idx_func < idx_btn:
        print("   ⚠️ A função está ANTES do botão (o JavaScript é executado linha por linha, então pode não estar disponível quando o botão é clicado).")
    else:
        print("   ✅ A função está DEPOIS do botão (ok para onclick).")
        
    # Mostra o bloco da função (primeiras 15 linhas)
    print("\n   📌 Início da função:")
    for linha in html[idx_func:idx_func+500].split("\n")[:15]:
        print(f"      {linha.strip()}")
else:
    print("   ❌ Função 'async function salvarRelatorioConsolidado' NÃO ENCONTRADA.")

# 2. Verifica se o botão tem o onclick correto
print("\n2. VERIFICANDO O BOTÃO:")
if 'onclick="salvarRelatorioConsolidado()"' in html:
    print("   ✅ O botão tem o onclick correto.")
    # Mostra a linha do botão
    for i, linha in enumerate(linhas):
        if 'btn-salvar-consolidado' in linha:
            print(f"      Linha {i+1}: {linha.strip()[:200]}")
            break
else:
    print("   ❌ O botão NÃO tem o onclick correto.")

# 3. Verifica se há um <script> quebrado antes do botão
print("\n3. VERIFICANDO SCRIPTS ANTES DO BOTÃO:")
idx_btn = html.find('btn-salvar-consolidado')
if idx_btn != -1:
    antes_btn = html[:idx_btn]
    # Conta os <script> e </script> antes do botão
    abre_script = antes_btn.count("<script")
    fecha_script = antes_btn.count("</script>")
    print(f"   <script> antes do botão: {abre_script}")
    print(f"   </script> antes do botão: {fecha_script}")
    if abre_script > fecha_script:
        print("   ⚠️ Há um <script> aberto antes do botão que não foi fechado! Isso quebra a página.")
    elif abre_script < fecha_script:
        print("   ⚠️ Há um </script> antes do botão sem <script> correspondente.")
    else:
        print("   ✅ Scripts balanceados antes do botão.")

# 4. Mostra as últimas linhas do HTML para ver se o script foi fechado corretamente
print("\n4. ÚLTIMAS 10 LINHAS DO HTML:")
for linha in linhas[-10:]:
    if linha.strip():
        print(f"   {linha.strip()[:200]}")

# 5. Verifica se há erro de sintaxe no último <script> (contagem de chaves)
print("\n5. VERIFICANDO CHAVES NO ÚLTIMO <script>:")
idx_ultimo_script = html.rfind("<script")
if idx_ultimo_script != -1:
    bloco_script = html[idx_ultimo_script:]
    abre_chaves = bloco_script.count("{")
    fecha_chaves = bloco_script.count("}")
    print(f"   Chaves abertas: {abre_chaves}")
    print(f"   Chaves fechadas: {fecha_chaves}")
    if abre_chaves != fecha_chaves:
        print("   ⚠️ Chaves desbalanceadas no último script!")
    else:
        print("   ✅ Chaves balanceadas no último script.")
