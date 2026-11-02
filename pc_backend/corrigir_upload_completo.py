import re

c = open('main.py', encoding='utf-8-sig').read()

# Padrão para encontrar a função upload_arquivo inteira
padrao = r'async def upload_arquivo\(.*?return \{"filename": file\.filename, "status": "sucesso"\}'

nova_funcao = '''async def upload_arquivo(file: UploadFile = File(...), tipo_relatorio: str = Form(None), ano: str = Form(None), periodo_tipo: str = Form(None), periodo_valor: str = Form(None)):
    import csv, io, json, sqlite3
    from datetime import datetime
    
    caminho = os.path.join(UPLOAD_DIR, file.filename)
    with open(caminho, "wb") as b: shutil.copyfileobj(file.file, b)
    
    mensagem = "Arquivo enviado com sucesso."
    
    # Se for Centro de Custos, processa o CSV e salva no banco
    if tipo_relatorio and tipo_relatorio.upper() == "CENTRO_CUSTOS":
        try:
            with open(caminho, "r", encoding="utf-8-sig") as f:
                decoded = f.read()
            reader = csv.DictReader(io.StringIO(decoded))
            centros = []
            for row in reader:
                nome = row.get("Centro de Custo") or row.get("centro_custo") or row.get("Nome") or row.get("nome") or ""
                valor_str = row.get("Valor") or row.get("valor") or row.get("Valor (R$)") or "0"
                valor_str = str(valor_str).replace("R$", "").replace(".", "").replace(",", ".").strip()
                try:
                    valor = float(valor_str)
                except:
                    valor = 0.0
                if nome.strip():
                    centros.append({"nome": nome.strip(), "valor": valor})
            
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
                mensagem = f"Centro de Custos importado com sucesso! ({len(centros)} centros)"
            else:
                mensagem = "CSV processado, mas nenhum centro encontrado."
        except Exception as e:
            mensagem = f"Erro ao processar CSV: {str(e)}"
    
    return {
        "status": "sucesso",
        "mensagem": mensagem,
        "arquivo": file.filename,
        "tipo_relatorio": tipo_relatorio,
        "dados_processados": centros if tipo_relatorio and tipo_relatorio.upper() == "CENTRO_CUSTOS" else []
    }'''

# Substitui a função
if re.search(padrao, c, re.DOTALL):
    c = re.sub(padrao, nova_funcao, c, flags=re.DOTALL)
    print("[OK] Função upload_arquivo substituída com sucesso!")
else:
    print("[AVISO] Padrão não encontrado. Tentando substituição manual...")
    # Tenta encontrar pelo início
    inicio = c.find("async def upload_arquivo")
    if inicio != -1:
        fim = c.find("import json", inicio)
        if fim != -1:
            c = c[:inicio] + nova_funcao + "\n" + c[fim:]
            print("[OK] Função substituída manualmente!")

open('main.py', 'w', encoding='utf-8').write(c)
