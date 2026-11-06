import urllib.request, json

print("=" * 70)
print("DIAGNÓSTICO: O QUE O RELATÓRIO VÊ")
print("=" * 70)

# 1. Busca o histórico (como o relatório faz)
print("\n--- 1. BUSCANDO HISTÓRICO ID 2 ---")
try:
    url_hist = "http://127.0.0.1:9994/historico_comparativo_despesas/2"
    with urllib.request.urlopen(url_hist) as r:
        hist_data = json.loads(r.read().decode())
    print(f"Chaves do histórico: {list(hist_data.keys())}")
    
    if "dados" in hist_data:
        dados = hist_data["dados"]
        if isinstance(dados, str):
            dados = json.loads(dados)
        print(f"Chaves dos dados: {list(dados.keys())}")
        
        if "atual" in dados:
            at = dados["atual"]
            print(f"\nChaves de 'atual': {list(at.keys())}")
            print(f"Quantidade de 'detalhes' em 'atual': {len(at.get('detalhes', []))}")
            
            if at.get("detalhes"):
                print("\nPrimeiros 2 detalhes do histórico:")
                for d in at["detalhes"][:2]:
                    print(f"  {d}")
            else:
                print("\n[PROBLEMA] O histórico NÃO tem 'detalhes'!")
                print("Isso significa que o histórico foi salvo ANTES da atualização da API.")
        else:
            print("\n[PROBLEMA] O histórico NÃO tem 'atual'!")
    else:
        print("\n[PROBLEMA] O histórico NÃO tem 'dados'!")
except Exception as e:
    print(f"[ERRO] {e}")

# 2. Busca a API direta
print("\n--- 2. BUSCANDO API DIRETA ---")
try:
    url_api = "http://127.0.0.1:9994/api/comparativo_despesas_v2/2026-TRIMESTRE-3"
    with urllib.request.urlopen(url_api) as r:
        api_data = json.loads(r.read().decode())
    
    if api_data.get("erro"):
        print(f"[ERRO na API] {api_data.get('mensagem')}")
    else:
        at_api = api_data.get("atual", {})
        print(f"Quantidade de 'detalhes' na API: {len(at_api.get('detalhes', []))}")
        if at_api.get("detalhes"):
            print("\nPrimeiros 2 detalhes da API:")
            for d in at_api["detalhes"][:2]:
                print(f"  {d}")
except Exception as e:
    print(f"[ERRO] {e}")

print("\n" + "=" * 70)
print("CONCLUSÃO")
print("=" * 70)
print("Se o histórico está vazio mas a API tem dados:")
print("  -> O histórico foi salvo ANTES da atualização da API.")
print("  -> Solução: salvar um novo histórico (clique em Confirmar e Salvar).")
