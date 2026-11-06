import re

arquivos = [
    "analise_bp.html",
    "analise_orcamentaria.html",
    "analise_financeira_bf.html",
    "analise_dfc.html",
    "analise_patrimonial.html",
]

print("=" * 70)
print("IDs DE INPUTS E BOTÕES DE VERIFICAR")
print("=" * 70)

for arq in arquivos:
    caminho = f"pc_frontend/{arq}"
    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()
    
    print(f"\n--- {arq} ---")
    
    # Procura IDs de selects e inputs
    ids = re.findall(r'<select[^>]*id=["\']([^"\']+)["\']', html)
    ids += re.findall(r'<input[^>]*id=["\']([^"\']+)["\']', html)
    print(f"  IDs de selects/inputs: {sorted(set(ids))}")
    
    # Procura botões que chamam funções de carregar/verificar
    botoes = re.findall(r'<button[^>]*onclick=["\']([^"\']*(?:carregar|verificar|buscar|load)[^"\']*)["\']', html, re.IGNORECASE)
    if not botoes:
        # Procura onclick genérico
        botoes = re.findall(r'<button[^>]*onclick=["\']([^"\']+)["\']', html)
    print(f"  Botões (onclick): {sorted(set(botoes))[:5]}")
    
    # Procura função JS que carrega dados
    funcs = re.findall(r'function\s+(\w*(?:carregar|verificar|buscar|load)\w*)', html, re.IGNORECASE)
    print(f"  Funções JS: {sorted(set(funcs))[:5]}")
