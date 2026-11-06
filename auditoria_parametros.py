import re

arquivos = [
    "analise_bp.html",
    "analise_orcamentaria.html",
    "analise_financeira_bf.html",
    "analise_dfc.html",
    "analise_patrimonial.html",
    "analise_comparativo_receitas.html",
    "analise_comparativo_despesas.html",
    "analise_centro_custos.html",
    "analise_custo_pessoal.html",
]

print("=" * 70)
print("PARÂMETRO DE URL E API USADOS POR CADA TELA")
print("=" * 70)

for arq in arquivos:
    caminho = f"pc_frontend/{arq}"
    try:
        with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()
    except:
        print(f"\n[ERRO] Não encontrado: {arq}")
        continue
    
    # Procura URLSearchParams ou window.location.search
    params = re.findall(r'URLSearchParams|location\.search|getParameter', html)
    
    # Procura chamadas fetch
    fetches = re.findall(r'fetch\(`?([^`\'")]+)', html)[:3]
    
    print(f"\n--- {arq} ---")
    print(f"  Parâmetro de URL: {'URLSearchParams' if params else 'não detectado'}")
    print(f"  Fetch (primeiros 3):")
    for f_ in fetches:
        print(f"    {f_[:80]}")
