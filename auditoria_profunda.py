import os
import re
import json
import urllib.request

print("=" * 80)
print("🔍 1. AUDITORIA DO BACKEND (O que a API está devolvendo?)")
print("=" * 80)

url = "http://localhost:9994/api/comparativo_receitas_v2/2026-TRIMESTRE-3"
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read().decode())
        
        print("✅ Resposta da API recebida com sucesso!")
        print(f"   Erro? {data.get('erro')}")
        print(f"   Realizado Total: {data.get('realizado_total')}")
        print(f"   Orçado Total:    {data.get('orcado_total')}")
        print(f"   Grupos no período atual: {len(data.get('grupos', []))}")
        
        if data.get('anterior'):
            print(f"   Grupos no período anterior: {len(data['anterior'].get('grupos', []))}")
            print(f"   Realizado Anterior: {data['anterior'].get('realizado_total')}")
        else:
            print("   ⚠️ A API NÃO RETORNOU O OBJETO 'anterior'!")
            
except Exception as e:
    print(f"❌ Erro ao chamar a API: {e}")
    print("   O servidor backend está rodando na porta 9994?")

print("\n" + "=" * 80)
print("🔍 2. AUDITORIA DO FRONTEND (O HTML ficou corrompido?)")
print("=" * 80)

html_path = "pc_frontend/analise_comparativo_receitas.html"
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# Verifica o balanceamento de chaves e parênteses no bloco de script
scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
if not scripts:
    print("❌ Nenhum bloco <script> encontrado no HTML!")

for i, script in enumerate(scripts):
    abre_chaves = script.count('{')
    fecha_chaves = script.count('}')
    abre_parenteses = script.count('(')
    fecha_parenteses = script.count(')')
    
    print(f"   Script {i+1}:")
    print(f"      Chaves: {abre_chaves} abertas, {fecha_chaves} fechadas {'✅' if abre_chaves == fecha_chaves else '❌ (DESBALANCEADO!)'}")
    print(f"      Parênteses: {abre_parenteses} abertos, {fecha_parenteses} fechados {'✅' if abre_parenteses == fecha_parenteses else '❌ (DESBALANCEADO!)'}")
    
    # Procura se a função renderizarTabela ainda está lá e se a variável 'anteriorMap' existe
    if "function renderizarTabela" in script:
        print("      ✅ Função renderizarTabela encontrada.")
        if "anteriorMap" in script:
            print("      ✅ Variável 'anteriorMap' encontrada.")
        else:
            print("      ⚠️ Variável 'anteriorMap' NÃO encontrada. A substituição pode ter falhado.")
    else:
        print("      ❌ Função renderizarTabela NÃO encontrada!")

# Mostra o trecho da função renderizarTabela para inspeção visual
idx = html.find("function renderizarTabela")
if idx != -1:
    print("\n" + "=" * 80)
    print("📄 TRECHO DA FUNÇÃO renderizarTabela NO HTML ATUAL:")
    print("=" * 80)
    # Pega 40 linhas a partir da função
    trecho = html[idx:idx+1500]
    for linha in trecho.split("\n")[:40]:
        print("   " + linha)
