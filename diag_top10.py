import urllib.request, json

url = "http://127.0.0.1:9994/api/comparativo_despesas_v2/2026-TRIMESTRE-3"
try:
    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read().decode())
    
    print("=" * 70)
    print("DIAGNÓSTICO: TOP 10 (CAMPO detalhes)")
    print("=" * 70)
    
    if data.get("erro"):
        print(f"[ERRO na API] {data.get('mensagem')}")
    else:
        at = data.get("atual", {})
        print(f"\nChaves do 'atual': {list(at.keys())}")
        print(f"Quantidade de detalhes: {len(at.get('detalhes', []))}")
        
        if at.get("detalhes"):
            print("\nPrimeiros 5 detalhes:")
            for d in at["detalhes"][:5]:
                print(f"  {d}")
        else:
            print("\n[AVISO] Campo 'detalhes' está VAZIO.")
            print("Isso significa que o backend não encontrou subgrupos com valor empenhado > 0.")
            
            print("\n--- GRUPOS QUE A API RETORNOU (para comparação) ---")
            for g in at.get("grupos", []):
                print(f"  {g.get('nome')}: empenhado={g.get('empenhado')}")
        
        print(f"\nTotal Empenhado (atual): {at.get('empenhado_total')}")
except Exception as e:
    print(f"[ERRO] Falha na requisição: {e}")
