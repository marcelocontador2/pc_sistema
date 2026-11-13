import urllib.request
import json
import re

# 1. Testa a API
print("=" * 60)
print("TESTE 1: API de Despesas")
print("=" * 60)
try:
    url = "http://127.0.0.1:9994/api/comparativo_despesas_v2/2026-TRIMESTRE-3"
    with urllib.request.urlopen(url, timeout=10) as r:
        data = json.loads(r.read().decode())
    print(f"Status: 200")
    print(f"Chaves: {list(data.keys())}")
    print(f"Tem 'atual'? {'atual' in data}")
    if 'atual' in data:
        print(f"Grupos: {len(data['atual'].get('grupos', []))}")
        print(f"Empenhado: {data['atual'].get('empenhado_total')}")
except Exception as e:
    print(f"ERRO: {e}")

# 2. Lê o HTML e verifica funções
print("\n" + "=" * 60)
print("TESTE 2: HTML - Funções e Botões")
print("=" * 60)
html = open('pc_frontend/analise_comparativo_despesas.html', 'r', encoding='utf-8').read()

funcoes = ['verificar', 'exibirSelecionado', 'renderizarTabela', 'atualizarCards']
for f in funcoes:
    if f'function {f}(' in html:
        print(f"✅ Função {f} existe")
    else:
        print(f"❌ Função {f} NÃO existe")

# Verifica o botão Verificar
if 'onclick="verificar()"' in html:
    print("✅ Botão Verificar tem onclick=verificar()")
else:
    print("❌ Botão Verificar NÃO tem onclick=verificar()")
    # Mostra como está o botão
    idx = html.find('Verificar')
    if idx != -1:
        print(f"Trecho do botão: {html[max(0,idx-100):idx+50]}")

# Mostra o bloco <script> (primeiros 1500 caracteres)
idx = html.find('<script>')
if idx != -1:
    print("\n--- Primeiros 1500 caracteres do <script> ---")
    print(html[idx:idx+1500])
else:
    print("❌ Bloco <script> NÃO encontrado")
