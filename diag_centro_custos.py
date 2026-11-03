import re, os

print("=" * 70)
print("DIAGNÓSTICO: ANÁLISE POR CENTRO DE CUSTOS")
print("=" * 70)

arquivo = r"pc_frontend\analise_centro_custos.html"

if not os.path.exists(arquivo):
    print(f"[ERRO] Arquivo {arquivo} não encontrado.")
else:
    c = open(arquivo, encoding="utf-8-sig").read()
    
    print("\n--- 1. BOTÕES COM 'PDF' ENCONTRADOS ---")
    botoes = re.findall(r'<button[^>]*>.*?PDF.*?</button>', c, re.IGNORECASE | re.DOTALL)
    for i, btn in enumerate(botoes):
        print(f"  [{i+1}] {btn.strip()[:200]}")
    if not botoes:
        print("  Nenhum botão de PDF encontrado.")

    print("\n--- 2. COMO O PDF É CHAMADO (ONCLICK/FUNÇÃO) ---")
    chamadas = re.findall(r'(?:onclick="[^"]*gerar[^"]*"|window\.open\([^)]*gerar[^)]*\)|fetch\([^)]*gerar[^)]*\))', c, re.IGNORECASE)
    for ch in chamadas:
        print(f"  {ch[:200]}")
    if not chamadas:
        print("  Nenhuma chamada de PDF encontrada no HTML.")

    print("\n--- 3. COMO O HISTÓRICO ESTÁ ESTRUTURADO ---")
    inputs = re.findall(r'<input[^>]*type=["\'](?:checkbox|radio)["\'][^>]*>', c, re.IGNORECASE)
    for inp in inputs[:5]:
        print(f"  {inp}")
    if not inputs:
        print("  Nenhum input de seleção (checkbox/radio) encontrado.")

print("\n" + "=" * 70)
print("ROTAS DE PDF DE CENTRO DE CUSTOS NO BACKEND (main.py)")
print("=" * 70)
c_back = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

matches = re.finditer(r'(@app\.(?:get|post)\(["\']([^"\']*centro_custos[^"\']*)["\']\).*?\ndef\s+([a-zA-Z0-9_]+)\([^)]*\))', c_back, re.DOTALL | re.IGNORECASE)
encontrou = False
for m in matches:
    rota = m.group(2)
    if "pdf" in rota.lower() or "gerar" in rota.lower():
        print(f"\nRota: {rota}")
        print(f"Função: {m.group(3)}")
        encontrou = True

if not encontrou:
    print("Nenhuma rota de PDF de Centro de Custos encontrada no backend.")
