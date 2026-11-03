import urllib.request
import json

print("=" * 70)
print("INSPECIONANDO O HISTÓRICO ID 32")
print("=" * 70)

try:
    req = urllib.request.Request("http://127.0.0.1:9994/historico_centro_custos/32")
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        
        print(f"Status: OK")
        print(f"Período: {data.get('periodo')}")
        
        dados = data.get('dados', {})
        if isinstance(dados, str):
            dados = json.loads(dados)
        
        print(f"Tem erro? {dados.get('erro')}")
        print(f"Periodo anterior: {dados.get('periodo_anterior')}")
        
        centros = dados.get('centros', [])
        centros_ant = dados.get('centros_anterior', [])
        
        print(f"\nQuantidade de centros ATUAIS: {len(centros)}")
        if centros:
            print("Primeiros 3 centros:")
            for c in centros[:3]:
                print(f"  - {c}")
        else:
            print("  [!!] LISTA VAZIA! O histórico foi salvo sem os dados dos centros.")
            
        print(f"\nQuantidade de centros ANTERIORES: {len(centros_ant)}")
        
except Exception as e:
    print(f"Erro: {e}")
