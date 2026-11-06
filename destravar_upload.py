import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_upload_destravar_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# 1. Remove o processamento do BP (se houver) e adiciona um return antecipado
# Procura o trecho onde salva o arquivo e adiciona um return logo apos
idx_salvar = c.find("# Salva o arquivo")
if idx_salvar != -1:
    # Encontra o fim do bloco de salvamento (proximo "if tipo_relatorio" ou "return")
    # Vamos adicionar um return antecipado para o BP
    trecho_antigo = '''    # Salva o arquivo
    caminho = os.path.join(UPLOAD_DIR, nome_arquivo)
    with open(caminho, "wb") as b:
        shutil.copyfileobj(file.file, b)'''
    
    trecho_novo = '''    # Salva o arquivo
    caminho = os.path.join(UPLOAD_DIR, nome_arquivo)
    with open(caminho, "wb") as b:
        shutil.copyfileobj(file.file, b)
    
    # Se for Balanco Patrimonial, retorna imediatamente (sem processar)
    if tipo_relatorio and "BALANCO_PATRIMONIAL" in tipo_relatorio.upper():
        return {"ok": True, "mensagem": f"Arquivo {nome_arquivo} salvo com sucesso!"}'''
    
    if trecho_antigo in c:
        c = c.replace(trecho_antigo, trecho_novo, 1)
        print("[OK] Return antecipado para o BP adicionado (sem processamento pesado).")
    else:
        print("[AVISO] Trecho de salvamento nao encontrado. Tentando variacao...")
        # Tenta encontrar o salvamento com indentacao diferente
        padrao = re.compile(r'(    # Salva o arquivo\s*\n\s*caminho = os\.path\.join\(UPLOAD_DIR, nome_arquivo\)\s*\n\s*with open\(caminho, "wb"\) as b:\s*\n\s*shutil\.copyfileobj\(file\.file, b\))', re.DOTALL)
        match = padrao.search(c)
        if match:
            c = c.replace(match.group(1), match.group(1) + '''
    
    # Se for Balanco Patrimonial, retorna imediatamente (sem processar)
    if tipo_relatorio and "BALANCO_PATRIMONIAL" in tipo_relatorio.upper():
        return {"ok": True, "mensagem": f"Arquivo {nome_arquivo} salvo com sucesso!"}''', 1)
            print("[OK] Return antecipado para o BP adicionado (variacao).")
        else:
            print("[ERRO] Nao foi possivel encontrar o trecho de salvamento.")

open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_upload_destravar_{ts}", back_path)
