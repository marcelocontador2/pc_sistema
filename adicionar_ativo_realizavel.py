import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_api_bp_ativo_real_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Verifica se a API ja tem o campo ativo_realizavel
if 'ativo_realizavel' in c:
    print("[AVISO] O campo 'ativo_realizavel' ja existe na API.")
else:
    print("[INFO] O campo 'ativo_realizavel' NAO existe. Adicionando...")
    
    # Procura a API do BP
    idx = c.find('@app.get("/api/analise_bp/{periodo}")')
    if idx == -1:
        print("[ERRO] API do BP nao encontrada.")
        exit(1)
    
    fim = c.find('@app', idx + 10)
    if fim == -1:
        fim = len(c)
    
    bloco = c[idx:fim]
    
    # Adiciona o campo ativo_realizavel na busca
    if 'ativo_realizavel_at, ativo_realizavel_ant = buscar_ativo("ATIVO REALIZÁVEL A LONGO PRAZO")' not in bloco:
        # Procura onde busca o ativo_nao_circulante
        idx_busca = bloco.find('ativo_nao_circ_at, ativo_nao_circ_ant = buscar_ativo("ATIVO NÃO CIRCULANTE")')
        if idx_busca != -1:
            fim_linha = bloco.find("\n", idx_busca) + 1
            bloco = bloco[:fim_linha] + '        ativo_realizavel_at, ativo_realizavel_ant = buscar_ativo("ATIVO REALIZÁVEL A LONGO PRAZO")\n' + bloco[fim_linha:]
            print("[OK] Busca do 'ativo_realizavel' adicionada.")
    
    # Adiciona o campo no dicionario de dados
    if '"ativo_realizavel"' not in bloco:
        idx_dados = bloco.find('"ativo_nao_circulante": {"atual": ativo_nao_circ_at, "anterior": ativo_nao_circ_ant},')
        if idx_dados != -1:
            fim_linha = bloco.find("\n", idx_dados) + 1
            bloco = bloco[:fim_linha] + '            "ativo_realizavel": {"atual": ativo_realizavel_at, "anterior": ativo_realizavel_ant},\n' + bloco[fim_linha:]
            print("[OK] Campo 'ativo_realizavel' adicionado ao dicionario de dados.")
    
    c = c[:idx] + bloco + c[fim:]
    open(back_path, "w", encoding="utf-8").write(c)
    
    try:
        ast.parse(open(back_path, encoding="utf-8").read())
        print("[OK] Sintaxe validada.")
    except SyntaxError as e:
        print(f"[ERRO] Sintaxe quebrada: {e}")
        shutil.copy2(f"{back_path}.bak_api_bp_ativo_real_{ts}", back_path)
