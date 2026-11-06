import urllib.request
import json

print("=" * 70)
print("DIAGNÓSTICO: ESTRUTURA DO JSON DO HISTÓRICO")
print("=" * 70)

# Tenta buscar o histórico ID 1 (ajuste se necessário)
historico_id = 1

try:
    url = f"http://127.0.0.1:9994/historico_comparativo_receitas/{historico_id}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        
        print(f"\nStatus: OK")
        print(f"Chaves principais do JSON: {list(data.keys())}")
        
        if "dados" in data:
            dados = data["dados"]
            if isinstance(dados, str):
                dados = json.loads(dados)
            print(f"\nTipo do objeto 'dados': {type(dados).__name__}")
            if isinstance(dados, dict):
                print(f"Chaves dentro de 'dados': {list(dados.keys())}")
                
                if "atual" in dados:
                    print(f"\nChaves de 'atual': {list(dados['atual'].keys())}")
                    print(f"Exemplo: realizado_total = {dados['atual'].get('realizado_total')}")
                    print(f"Exemplo: orcado_total = {dados['atual'].get('orcado_total')}")
                    print(f"Exemplo: percentual_total = {dados['atual'].get('percentual_total')}")
                else:
                    print("\n[AVISO] Não tem 'atual' dentro de 'dados'.")
            else:
                print(f"O objeto 'dados' não é dicionário, é: {dados}")
        else:
            print("\n[AVISO] Não tem a chave 'dados' no JSON. O objeto todo é:")
            print(json.dumps(data, indent=2)[:1000])
            
except Exception as e:
    print(f"\n[ERRO] Falha na requisição: {e}")
    print("Verifique se o servidor está rodando na porta 9994.")
