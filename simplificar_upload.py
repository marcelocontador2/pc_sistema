import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_upload_simples_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Localiza a rota /upload
idx = c.find('async def upload_arquivo(')
if idx == -1:
    print("[ERRO] Funcao upload_arquivo nao encontrada.")
    exit(1)

fim = c.find('@app', idx + 20)
if fim == -1:
    fim = len(c)

# Nova rota ainda mais simples: le o arquivo com await e salva
nova_rota = '''async def upload_arquivo(
    file: UploadFile = File(...),
    tipo_relatorio: str = Form(None),
    ano: str = Form(None),
    periodo_tipo: str = Form(None),
    periodo_valor: str = Form(None)
):
    import os
    from datetime import datetime
    
    # Define o nome padrao
    nome_arquivo = file.filename
    periodo_str = f"{ano}_{periodo_tipo}_{periodo_valor}" if ano and periodo_tipo and periodo_valor else "2026_TRIMESTRE_3"
    
    if tipo_relatorio:
        tipo = tipo_relatorio.upper()
        if "BALANCO_PATRIMONIAL" in tipo or "BP" == tipo:
            nome_arquivo = f"BALANCO_PATRIMONIAL_{periodo_str}.csv"
        elif "BALANCETE" in tipo:
            nome_arquivo = f"BALANCETE_{periodo_str}.csv"
        elif "BALANCO_ORCAMENTARIO" in tipo:
            nome_arquivo = f"BALANCO_ORCAMENTARIO_{periodo_str}.csv"
        elif "BALANCO_FINANCEIRO" in tipo:
            nome_arquivo = f"BALANCO_FINANCEIRO_{periodo_str}.csv"
        elif "DFC" in tipo:
            nome_arquivo = f"DFC_{periodo_str}.csv"
        elif "DVP" in tipo:
            nome_arquivo = f"DVP_{periodo_str}.csv"
        elif "DMPL" in tipo:
            nome_arquivo = f"DMPL_{periodo_str}.csv"
        elif "CENTRO_CUSTOS" in tipo:
            nome_arquivo = f"CENTRO_CUSTOS_{periodo_str}.csv"
        elif "COMPARATIVO_RECEITAS" in tipo:
            nome_arquivo = f"COMPARATIVO_RECEITAS_{periodo_str}.csv"
        elif "COMPARATIVO_DESPESAS" in tipo:
            nome_arquivo = f"COMPARATIVO_DESPESAS_{periodo_str}.csv"
    
    # Salva o arquivo (le com await, escreve com open)
    caminho = os.path.join(UPLOAD_DIR, nome_arquivo)
    conteudo = await file.read()
    with open(caminho, "wb") as f:
        f.write(conteudo)
    
    return {"ok": True, "mensagem": f"Arquivo {nome_arquivo} importado com sucesso!"}

'''

c = c[:idx] + nova_rota + c[fim:]
open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Rota /upload simplificada (usa await file.read() em vez de shutil).")
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_upload_simples_{ts}", back_path)
