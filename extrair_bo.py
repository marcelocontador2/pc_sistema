arq = r"pc_backend\main.py"
with open(arq, "r", encoding="utf-8") as f:
    linhas = f.readlines()

with open("trecho_pdf_bo.txt", "w", encoding="utf-8") as out:
    indice_inicio = -1
    # Procura a função que gera o PDF do Balanço Orçamentário
    for i, linha in enumerate(linhas):
        if "ANALISE DO BALANCO ORCAMENTARIO" in linha.upper() or "ANALISE ORCAMENTARIA" in linha.upper():
            indice_inicio = i
            break
            
    if indice_inicio != -1:
        # Pega 100 linhas a partir do cabeçalho para ver a tabela inteira
        fim = min(len(linhas), indice_inicio + 120)
        for i in range(indice_inicio, fim):
            out.write(f"{i+1}: {linhas[i]}")
    else:
        out.write("Não encontrei a função do Balanço Orçamentário no main.py.")

print("[OK] Trecho do BO extraído para 'trecho_pdf_bo.txt'")
