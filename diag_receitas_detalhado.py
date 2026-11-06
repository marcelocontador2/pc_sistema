import urllib.request
import json

print("=" * 70)
print("DIAGNÓSTICO DETALHADO: O QUE TEM DENTRO DE 'receitas'")
print("=" * 70)

historico_id = 1
url = f"http://127.0.0.1:9994/historico_comparativo_receitas/{historico_id}"

try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        dados = data["dados"]
        if isinstance(dados, str):
            dados = json.loads(dados)
        
        receitas = dados.get("receitas", [])
        print(f"\nQuantidade de receitas: {len(receitas)}")
        
        if receitas:
            print("\n--- PRIMEIRO ITEM (estrutura das chaves) ---")
            print(json.dumps(receitas[0], indent=2, ensure_ascii=False))
            
            print("\n--- TODOS OS NOMES E VALORES ---")
            for r in receitas:
                nome = r.get('nome', '?')
                realizado = r.get('realizado', 0)
                orcado = r.get('orcado', 0)
                print(f"  {nome}: realizado={realizado}, orcado={orcado}")
        
        # Verifica se tem dados do período anterior em algum lugar
        print("\n--- PROCURANDO DADOS DO PERÍODO ANTERIOR ---")
        if 'receitas_anterior' in dados:
            print(f"Tem 'receitas_anterior' com {len(dados['receitas_anterior'])} itens")
        elif 'anterior' in dados:
            print(f"Tem 'anterior': {dados['anterior']}")
        else:
            print("NÃO tem dados do período anterior no histórico. Só tem a lista 'receitas' atual.")
            
except Exception as e:
    print(f"Erro: {e}")


print("\n" + "=" * 70)
print("COMPARANDO COM A API NORMAL")
print("=" * 70)

try:
    url_api = "http://127.0.0.1:9994/api/comparativo_receitas_v2/2026-TRIMESTRE-3"
    req = urllib.request.Request(url_api)
    with urllib.request.urlopen(req) as response:
        data_api = json.loads(response.read().decode())
        print(f"Chaves da API normal: {list(data_api.keys())}")
        if 'atual' in data_api:
            print(f"Chaves de atual: {list(data_api['atual'].keys())}")
        if 'anterior' in data_api:
            print(f"Chaves de anterior: {list(data_api['anterior'].keys())}")
except Exception as e:
    print(f"Erro: {e}")
