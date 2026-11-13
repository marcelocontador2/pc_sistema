import urllib.request
import json

print("=" * 80)
print("🔍 DIAGNÓSTICO COMPLETO - TELA DE DESPESAS")
print("=" * 80)

# 1. Testa a rota de verificar (API de despesas)
print("\n📡 1. Testando GET /api/comparativo_despesas_v2/2026-TRIMESTRE-3")
try:
    with urllib.request.urlopen("http://127.0.0.1:9994/api/comparativo_despesas_v2/2026-TRIMESTRE-3", timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    print(f"   ✅ Status: 200")
    print(f"   Chaves: {list(data.keys())}")
    print(f"   erro: {data.get('erro')}")
    if data.get('atual'):
        print(f"   atual.grupos: {len(data['atual'].get('grupos', []))} itens")
        print(f"   atual.empenhado_total: {data['atual'].get('empenhado_total')}")
        print(f"   atual.orcado_total: {data['atual'].get('orcado_total')}")
    if data.get('anterior'):
        print(f"   anterior.grupos: {len(data['anterior'].get('grupos', []))} itens")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 2. Testa a rota de histórico (lista)
print("\n📡 2. Testando GET /historico_comparativo_despesas")
try:
    with urllib.request.urlopen("http://127.0.0.1:9994/historico_comparativo_despesas", timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    print(f"   ✅ Status: 200 | {len(data)} registros")
    for i, h in enumerate(data[:3]):
        print(f"   {i+1}. ID={h.get('id')} | Período={h.get('periodo')}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 3. Testa a rota de exibir (histórico por ID)
print("\n📡 3. Testando GET /historico_comparativo_despesas/1")
try:
    with urllib.request.urlopen("http://127.0.0.1:9994/historico_comparativo_despesas/1", timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    print(f"   ✅ Status: 200")
    print(f"   Chaves: {list(data.keys())}")
    if data.get('dados'):
        dados = data['dados']
        if isinstance(dados, str):
            dados = json.loads(dados)
        print(f"   dados tem 'atual'? {'atual' in dados}")
        if 'atual' in dados:
            print(f"   atual.grupos: {len(dados['atual'].get('grupos', []))} itens")
            print(f"   atual.empenhado_total: {dados['atual'].get('empenhado_total')}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 4. Testa a rota de PDF
print("\n📡 4. Testando GET /gerar_pdf_comparativo_despesas/1")
try:
    with urllib.request.urlopen("http://127.0.0.1:9994/gerar_pdf_comparativo_despesas/1", timeout=15) as response:
        content_type = response.headers.get('Content-Type', '')
        content_length = len(response.read())
    print(f"   ✅ Status: 200 | Tipo: {content_type} | Tamanho: {content_length} bytes")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 5. Testa a rota de salvar
print("\n📡 5. Testando POST /api/comparativo_despesas_v2/2026-TRIMESTRE-3/salvar")
try:
    req = urllib.request.Request(
        "http://127.0.0.1:9994/api/comparativo_despesas_v2/2026-TRIMESTRE-3/salvar",
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    print(f"   ✅ Status: 200 | {data}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 6. Testa a rota de excluir (mas não executa de verdade)
print("\n📡 6. Verificando se a rota de excluir existe (POST /excluir_multiplos_comparativo_despesas)")
print("   (não executando para não apagar dados)")
