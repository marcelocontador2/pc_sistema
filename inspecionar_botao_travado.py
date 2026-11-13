import re

caminho_html = "pc_frontend/relatorio_consolidado.html"
print("🔍 INSPECIONANDO O HTML PARA ERROS DE JAVASCRIPT...\n")

with open(caminho_html, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Verifica se a função está dentro de um bloco (ex: DOMContentLoaded) que a torna local
if "function salvarRelatorioConsolidado" in html:
    # Encontra a posição da função
    idx = html.find("function salvarRelatorioConsolidado")
    # Verifica se há um "document.addEventListener" antes dela, o que pode indicar que ela está dentro de um bloco
    antes = html[:idx]
    if "document.addEventListener" in antes or "window.onload" in antes:
        print("⚠️ A função 'salvarRelatorioConsolidado' pode estar dentro de um bloco que a torna local (não global).")
    else:
        print("✅ A função 'salvarRelatorioConsolidado' está no escopo global.")
else:
    print("❌ Função 'salvarRelatorioConsolidado' NÃO ENCONTRADA.")

# 2. Verifica se há erros de sintaxe comuns (chaves desbalanceadas) no script
# Conta as chaves { } dentro das tags <script>
scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
for i, script in enumerate(scripts):
    abre = script.count('{')
    fecha = script.count('}')
    if abre != fecha:
        print(f"⚠️ Script {i+1}: Chaves desbalanceadas! Abre: {abre}, Fecha: {fecha}")
    else:
        print(f"✅ Script {i+1}: Chaves balanceadas ({abre} abre, {fecha} fecha).")

# 3. Mostra a linha do botão e as 5 linhas seguintes (contexto)
print("\n📌 CONTEXTO DO BOTÃO 'Confirmar e Salvar':")
linhas = html.split("\n")
for i, linha in enumerate(linhas):
    if 'btn-salvar-consolidado' in linha:
        inicio = max(0, i-3)
        fim = min(len(linhas), i+5)
        for j in range(inicio, fim):
            marcador = ">>> " if j == i else "    "
            print(f"{marcador}Linha {j+1}: {linhas[j].strip()}")
        break

# 4. Mostra a função salvarRelatorioConsolidado (as primeiras 10 linhas)
print("\n📌 INÍCIO DA FUNÇÃO 'salvarRelatorioConsolidado':")
idx_func = html.find("function salvarRelatorioConsolidado")
if idx_func != -1:
    bloco = html[idx_func:idx_func+800]
    for linha in bloco.split("\n")[:12]:
        print(f"   {linha.strip()}")
