import re

c = open('main.py', encoding='utf-8-sig').read()

# Padrão para encontrar a função upload_arquivo inteira
padrao = r'async def upload_arquivo\(.*?return \{.*?\}'

nova_funcao = '''async def upload_arquivo(
    file: UploadFile = File(...),
    tipo_relatorio: str = Form(None),
    ano: str = Form(None),
    periodo_tipo: str = Form(None),
    periodo_valor: str = Form(None)
):
    import os, shutil, csv, io, json, sqlite3
    from datetime import datetime
    
    # Variáveis iniciais
    dados_processados = []
    mensagem = "Arquivo enviado com sucesso."
    centros = []
    
    # Define o nome padronizado
    nome_arquivo = file.filename
    if tipo_relatorio and tipo_relatorio.upper() == "CENTRO_CUSTOS":
        periodo_str = f"{ano}_{periodo_tipo}_{periodo_valor}" if ano and periodo_tipo and periodo_valor else "2026_TRIMESTRE_3"
        nome_arquivo = f"CENTRO_CUSTOS_{periodo_str}.csv"
    
    # Salva o arquivo
    caminho = os.path.join(UPLOAD_DIR, nome_arquivo)
    with open(caminho, "wb") as b:
        shutil.copyfileobj(file.file, b)
    
    # Processa Centro de Custos
    if tipo_relatorio and tipo_relatorio.upper() == "CENTRO_CUSTOS":
        try:
            # Tenta ler como UTF-8, se falhar, tenta como ANSI (latin-1)
            try:
                with open(caminho, "r", encoding="utf-8-sig") as f:
                    linhas = f.readlines()
            except UnicodeDecodeError:
                with open(caminho, "r", encoding="latin-1") as f:
                    linhas = f.readlines()
            
            # Encontra a linha de cabeçalho (que começa com "Centro de Custo x Conta")
            inicio_dados = 0
            for i, linha in enumerate(linhas):
                if "Centro de Custo x Conta" in linha:
                    inicio_dados = i + 1
                    break
            
            # Pula a linha do "COFEN/BR" se existir
            if inicio_dados < len(linhas) and "COFEN/BR" in linhas[inicio_dados]:
                inicio_dados += 1
                
            # Processa as linhas de dados
            for linha in linhas[inicio_dados:]:
                if ";" in linha:
                    partes = linha.strip().split(";")
                else:
                    partes = linha.strip().split(",")
                
                if len(partes) < 2:
                    continue
                
                nome = partes[0].strip().strip('"')
                if not nome or "TOTAL" in nome.upper() or nome.startswith("Página"):
                    continue
                
                # Pega o último valor numérico válido da linha
                valor = 0.0
                for parte in reversed(partes):
                    parte_limpa = parte.strip().strip('"').replace(".", "").replace(",", ".")
                    try:
                        valor = float(parte_limpa)
                        if valor > 0:
                            break
                    except:
                        continue
                
                centros.append({"nome": nome, "valor": valor})
            
            if centros:
                # Salva no banco de dados
                db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                cur.execute("""CREATE TABLE IF NOT EXISTS historico_centro_custos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, dados_json TEXT)""")
                periodo = f"{ano}-{periodo_tipo}-{periodo_valor}" if ano and periodo_tipo and periodo_valor else "2026-TRIMESTRE-3"
                data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                cur.execute("INSERT INTO historico_centro_custos (periodo, data_geracao, dados_json) VALUES (?, ?, ?)",
                           (periodo, data_geracao, json.dumps({"centros": centros})))
                conn.commit()
                conn.close()
                dados_processados = centros
                mensagem = f"Centro de Custos importado com sucesso! ({len(centros)} centros) - Arquivo: {nome_arquivo}"
            else:
                mensagem = "CSV processado, mas nenhum centro encontrado. Verifique o formato."
        except Exception as e:
            mensagem = f"Erro ao processar CSV: {str(e)}"
    
    return {
        "status": "sucesso",
        "mensagem": mensagem,
        "arquivo": nome_arquivo,
        "tipo_relatorio": tipo_relatorio,
        "dados_processados": dados_processados
    }'''

# Substitui a função
if re.search(padrao, c, re.DOTALL):
    c = re.sub(padrao, nova_funcao, c, flags=re.DOTALL)
    print("[OK] Função upload_arquivo reescrita do zero!")
else:
    print("[ERRO] Função upload_arquivo não encontrada.")

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] main.py atualizado!")
