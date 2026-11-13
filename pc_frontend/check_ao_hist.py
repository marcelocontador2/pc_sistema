import re

with open("analise_orcamentaria.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== ROTA CHAMADA NO FRONTEND (analise_orcamentaria.html) ===")
match = re.search(r'function carregarHistorico\(\)\s*\{.*?(?=\n\s*function|\Z)', s, re.DOTALL)
if match:
    bloco = match.group(0)
    # Procura o fetch
    fetches = re.findall(r'fetch\([\'"`]([^\'"`]+)[\'"`]\)', bloco)
    for f in fetches:
        print(f"  - Rota fetch: {f}")
    
    # Verifica o catch de erro
    if "catch" in bloco:
        print("  -> O frontend TEM um catch de erro (por isso mostra 'Erro ao carregar.').")
else:
    print("Função carregarHistorico não encontrada.")
