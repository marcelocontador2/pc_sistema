import re

c = open('main.py', encoding='utf-8-sig').read()

# Remove a função antiga (padrão robusto)
padrao = r'async def upload_arquivo\(.*?return \{.*?\}'
c = re.sub(padrao, '', c, flags=re.DOTALL)

# Adiciona a nova função
nova_funcao = '''async def upload_arquivo(
    file: UploadFile = File(...),
    tipo_relatorio: str = Form(None),
    ano: str = Form(None),
    periodo_tipo: str = Form(None),
    periodo_valor: str = Form(None)
):
    import os, shutil, csv, io, json, sqlite3
    from datetime import datetime
    
    # Define o nome padronizado
    nome_arquivo = file.filename
    if tipo_relatorio and tipo_relatorio.upper() == "CENTRO_CUSTOS":
        periodo_str = f"{ano}_{periodo_tipo}_{periodo_valor}" if ano and periodo_tipo and periodo_valor else "2026_TRIMESTRE_3"
        nome_arquivo = f"CENTRO_CUSTOS_{periodo_str}.csv"
    
    caminho = os.path.join(UPLOAD_DIR, nome_arquivo)
    with open(caminho, "wb") as b:
        shutil.copyfileobj(file.file, b)
    
    mensagem = f"Arquivo '{nome_arquivo}' salvo com sucesso."
    dados_processados = []
    
    # Processa Centro de Custos
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
                dados_processados = centros
                mensagem = f"Centro de Custos importado com sucesso! ({len(centros)} centros) - Arquivo: {nome_arquivo}"
            else:
                mensagem = "CSV processado, mas nenhum centro encontrado."
        except Exception as e:
            mensagem = f"Erro ao processar CSV: {str(e)}"
    
    return {
        "status": "sucesso",
        "mensagem": mensagem,
        "arquivo": nome_arquivo,
        "tipo_relatorio": tipo_relatorio,
        "dados_processados": dados_processados
    }'''

# Adiciona a nova função antes do "import json"
if 'import json' in c:
    c = c.replace('import json', nova_funcao + '\nimport json')
else:
    c += '\n' + nova_funcao

# Garante os imports
if "from fastapi import" in c:
    for imp in ["Form", "UploadFile", "File"]:
        if imp not in c:
            c = c.replace("from fastapi import", f"from fastapi import {imp},")

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] Rota /upload corrigida com nome padronizado e resposta completa!")
