import re

with open(r"pc_backend\main.py", "r", encoding="utf-8") as f:
    codigo = f.read()

for nome_func in ["gerar_pdf_analise_financeira_bf", "gerar_pdf_analise_dfc"]:
    print(f"\n{'='*60}")
    print(f"FUNÇÃO: {nome_func}")
    print('='*60)
    
    # Extrai o bloco da função
    idx = codigo.find(f"def {nome_func}(")
    if idx == -1:
        print(f"[ERRO] Função {nome_func} não encontrada.")
        continue
    
    # Encontra o próximo @app ou def
    fim = codigo.find("\n@app.", idx)
    if fim == -1:
        fim = codigo.find("\ndef ", idx + 10)
    if fim == -1:
        fim = idx + 6000
    
    bloco = codigo[idx:fim]
    
    # Mostra quantas vezes "add_font" e "set_font" aparecem
    print(f"Ocorrências de 'add_font': {bloco.count('add_font')}")
    print(f"Ocorrências de 'set_font': {bloco.count('set_font')}")
    print(f"Ocorrências de 'Helvetica': {bloco.count('Helvetica')}")
    print(f"Ocorrências de 'DejaVu': {bloco.count('DejaVu')}")
    print(f"Ocorrências de 'Arial': {bloco.count('Arial')}")
    
    # Mostra o trecho do FPDF inicial
    print("\n--- Trecho inicial (primeiras linhas da função) ---")
    linhas = bloco.split("\n")
    for l in linhas[:30]:
        print(l)
    
    # Mostra as chamadas set_font (contexto)
    print("\n--- Chamadas set_font ---")
    for m in re.finditer(r'set_font\([^)]+\)', bloco):
        print(f"  {m.group(0)}")
