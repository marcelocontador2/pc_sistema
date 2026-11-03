import re

print("=" * 70)
print("DIAGNÓSTICO: CUSTO DE PESSOAL")
print("=" * 70)

# 1. Vamos olhar o arquivo principal (analise_custo_pessoal.html)
arquivo = r"pc_frontend\analise_custo_pessoal.html"
try:
    c = open(arquivo, encoding="utf-8-sig").read()
    
    print("\n--- BOTÕES DE PDF ENCONTRADOS ---")
    # Procura botões com "PDF" no texto
    botoes = re.findall(r'<button[^>]*>.*?PDF.*?</button>', c, re.IGNORECASE | re.DOTALL)
    for i, btn in enumerate(botoes):
        print(f"[{i+1}] {btn.strip()[:200]}")
        
    print("\n--- COMO O PDF É CHAMADO (ONCLICK/FUNÇÃO) ---")
    # Procura chamadas que tenham 'gerar_pdf'
    chamadas = re.findall(r'(?:onclick|window\.open|fetch)\([^)]*gerar_pdf[^)]*\)', c, re.IGNORECASE)
    for ch in chamadas:
        print(f"  {ch[:200]}")

    print("\n--- COMO O HISTÓRICO ESTÁ ESTRUTURADO ---")
    # Procura inputs de seleção
    inputs = re.findall(r'<input[^>]*type=["\'](?:checkbox|radio)["\'][^>]*>', c, re.IGNORECASE)
    for inp in inputs[:5]: # Mostra só os 5 primeiros para não lotar
        print(f"  {inp}")

except Exception as e:
    print(f"Erro ao ler {arquivo}: {e}")

print("\n" + "=" * 70)
print("COMO A ROTA DO PDF ESTÁ NO BACKEND (main.py)")
print("=" * 70)
c_back = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

# Procura a rota de PDF do Custo Pessoal
match = re.search(r'(@app\.get\("/gerar_pdf_custo_pessoal[^"]*"\).*?)(?=\n@app\.|\Z)', c_back, re.DOTALL)
if match:
    print(match.group(1).strip()[:1000])
else:
    print("Rota não encontrada.")
