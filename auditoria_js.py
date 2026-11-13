import urllib.request
import json
import re

print("=" * 70)
print("AUDITORIA PROFUNDA - TELA DE DESPESAS")
print("=" * 70)

# 1. Testa a API
print("\n1. API de despesas:")
try:
    url = "http://127.0.0.1:9994/api/comparativo_despesas_v2/2026-TRIMESTRE-3"
    with urllib.request.urlopen(url, timeout=10) as r:
        data = json.loads(r.read().decode())
    print(f"   Status: 200")
    print(f"   Tem 'atual'? {'atual' in data}")
    if 'atual' in data:
        print(f"   Grupos: {len(data['atual'].get('grupos', []))}")
        print(f"   Empenhado: {data['atual'].get('empenhado_total')}")
        print(f"   Tipos dos campos:")
        for k, v in data['atual'].items():
            if k != 'grupos' and k != 'detalhes':
                print(f"     {k}: {type(v).__name__} = {v}")
except Exception as e:
    print(f"   ERRO: {e}")

# 2. Lê o HTML servido e verifica erros de sintaxe no JS
print("\n2. HTML servido pelo backend:")
try:
    with urllib.request.urlopen("http://127.0.0.1:9994/analise_comparativo_despesas", timeout=10) as r:
        html = r.read().decode("utf-8")
    print(f"   Tamanho: {len(html)} caracteres")
    
    # Extrai o script
    idx_script = html.find('<script>')
    idx_fim = html.find('</script>', idx_script)
    script = html[idx_script+8:idx_fim]
    
    print(f"   Tamanho do script: {len(script)} caracteres")
    
    # Verifica balanceamento de chaves e parênteses
    abre_chaves = script.count('{')
    fecha_chaves = script.count('}')
    abre_parenteses = script.count('(')
    fecha_parenteses = script.count(')')
    abre_colchetes = script.count('[')
    fecha_colchetes = script.count(']')
    
    print(f"   Chaves: {abre_chaves} abertas, {fecha_chaves} fechadas {'✅' if abre_chaves == fecha_chaves else '❌'}")
    print(f"   Parênteses: {abre_parenteses} abertos, {fecha_parenteses} fechados {'✅' if abre_parenteses == fecha_parenteses else '❌'}")
    print(f"   Colchetes: {abre_colchetes} abertos, {fecha_colchetes} fechados {'✅' if abre_colchetes == fecha_colchetes else '❌'}")
    
    # Verifica se há template strings não fechadas
    crases = script.count('`')
    print(f"   Template strings (crases): {crases} {'✅ (par)' if crases % 2 == 0 else '❌ (ímpar!)'}")
    
    # Verifica se há erros comuns
    print("\n   Verificando erros comuns no JS:")
    if 'data.atual' in script:
        print("   ✅ Usa data.atual")
    if 'data.grupos' in script and 'data.atual.grupos' not in script:
        print("   ⚠️ Usa data.grupos (pode estar errado)")
    
    # Mostra a função verificar
    idx_ver = script.find('function verificar(')
    if idx_ver != -1:
        # Pega até a próxima function
        idx_prox = script.find('function ', idx_ver + 10)
        if idx_prox == -1:
            idx_prox = len(script)
        print("\n   --- Função verificar() ---")
        print(script[idx_ver:idx_prox])
        
except Exception as e:
    print(f"   ERRO: {e}")

# 3. Verifica se há problemas de cache
print("\n3. Verificando se o HTML local é igual ao servido:")
try:
    html_local = open('pc_frontend/analise_comparativo_despesas.html', 'r', encoding='utf-8').read()
    with urllib.request.urlopen("http://127.0.0.1:9994/analise_comparativo_despesas", timeout=10) as r:
        html_servido = r.read().decode("utf-8")
    
    if len(html_local) == len(html_servido):
        print(f"   ✅ Tamanhos iguais ({len(html_local)} caracteres)")
    else:
        print(f"   ⚠️ Tamanhos diferentes: local={len(html_local)}, servido={len(html_servido)}")
        
except Exception as e:
    print(f"   ERRO: {e}")
