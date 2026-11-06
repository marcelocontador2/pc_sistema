import re, shutil, datetime

arquivo = r"pc_backend\main.py"
shutil.copy2(arquivo, f"pc_backend\\main_backup_dup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arquivo, "r", encoding="utf-8") as f:
    codigo = f.read()

print("--- ANALISANDO DUPLICATAS ---")
print(f"api_panorama: {len(re.findall(r'async def api_panorama\(periodo: str\):', codigo))} definicoes")
print(f"salvar_panorama: {len(re.findall(r'async def salvar_panorama\(periodo: str\):', codigo))} definicoes")

# =========================================================
# 1. LIMPAR E RECRIAR api_panorama
# =========================================================
padrao_api = re.compile(r'async def api_panorama\(periodo: str\):.*?(?=\n@app\.|\n@app\.get|\Z)', re.DOTALL)
matches_api = list(padrao_api.finditer(codigo))

nova_funcao_api = '''async def api_panorama(periodo: str):
    try:
        import sqlite3, json, os
        from matriz_integridade import _limpar_valor
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        def buscar_no_banco(tipo):
            nome = f"{tipo}_{periodo.replace('-', '_')}.csv"
            cursor.execute("SELECT dados_json FROM arquivos_importados WHERE nome_arquivo = ?", (nome,))
            row = cursor.fetchone()
            return json.loads(row[0]) if row else []
            
        demonstrativos = {
            "BALANCO_PATRIMONIAL": "Balanço Patrimonial",
            "BALANCO_ORCAMENTARIO": "Balanço Orçamentário",
            "BALANCO_FINANCEIRO": "Balanço Financeiro",
            "DFC": "Demonstração do Fluxo de Caixa",
            "DVP": "Demonstração das Variações Patrimoniais",
            "DMPL": "Demonstração das Mutações do PL",
        }
        faltando = []
        for tipo, nome in demonstrativos.items():
            if not buscar_no_banco(tipo):
                faltando.append(nome)
        if faltando:
            conn.close()
            return {"erro": "faltando", "pecas": faltando}
            
        l_bp = buscar_no_banco("BALANCO_PATRIMONIAL")
        l_bo = buscar_no_banco("BALANCO_ORCAMENTARIO")
        l_dvp = buscar_no_banco("DVP")
        
        def buscar(linhas, termos):
            for p in linhas:
                for termo in termos:
                    termo_upper = termo.upper()
                    for col_espec in [0, 3]:
                        if len(p) > col_espec and termo_upper in str(p[col_espec]).upper():
                            col_valor = col_espec + 1
                            if len(p) > col_valor:
                                try:
                                    v = abs(_limpar_valor(p[col_valor]))
                                    if v > 0:
                                        return v
                                except:
                                    pass
            return 0.0
            
        def buscar_exato(linhas, termo_exato):
            for p in linhas:
                for col_espec in [0, 3]:
                    if len(p) > col_espec and str(p[col_espec]).strip().upper() == termo_exato.upper():
                        col_valor = col_espec + 1
                        if len(p) > col_valor:
                            try:
                                v = abs(_limpar_valor(p[col_valor]))
                                if v > 0:
                                    return v
                            except:
                                pass
            return 0.0

        passivo_total = buscar_exato(l_bp, "TOTAL DO PASSIVO")
        if passivo_total == 0.0:
            passivo_total = buscar(l_bp, ["TOTAL DO PASSIVO", "PASSIVO TOTAL"])
            
        pl = buscar_exato(l_bp, "TOTAL DO PATRIMÔNIO LÍQUIDO")
        if pl == 0.0:
            pl = buscar_exato(l_bp, "TOTAL DO PATRIMONIO LIQUIDO")
        if pl == 0.0:
            pl = buscar(l_bp, ["TOTAL DO PATRIMÔNIO LÍQUIDO", "TOTAL DO PATRIMONIO LIQUIDO"])
            
        ativo_total = buscar_exato(l_bp, "TOTAL")
        if ativo_total == 0.0:
            ativo_total = buscar(l_bp, ["TOTAL DO ATIVO", "ATIVO TOTAL"])
        if ativo_total == 0.0:
            ativo_total = passivo_total + pl
            
        caixa_bp = buscar(l_bp, ["CAIXA E EQUIVALENTES", "CAIXA E EQUIVALENTE"])
        superavit_financeiro = buscar(l_bp, ["SUPERÁVIT FINANCEIRO", "SUPERAVIT FINANCEIRO"])
        
        receita_realizada = buscar(l_bo, ["TOTAL DAS RECEITAS", "RECEITAS REALIZADAS", "RECEITA REALIZADA", "TOTAL DA RECEITA", "RECEITAS"])
        despesa_empenhada = buscar(l_bo, ["TOTAL DAS DESPESAS", "DESPESAS EMPENHADAS", "DESPESA EMPENHADA", "TOTAL DA DESPESA", "DESPESAS"])
        superavit_orcamentario = receita_realizada - despesa_empenhada
        
        total_vpa = buscar(l_dvp, ["Total das Variações Ativas", "TOTAL DAS VARIACOES ATIVAS", "VARIAÇÕES ATIVAS"])
        total_vpd = buscar(l_dvp, ["Total das Variações Passivas", "TOTAL DAS VARIACOES PASSIVAS", "VARIAÇÕES PASSIVAS"])
        superavit_patrimonial = total_vpa - total_vpd
        
        conn.close()
        
        return {
            "ativo_total": ativo_total,
            "passivo_total": passivo_total,
            "patrimonio_liquido": pl,
            "caixa_bp": caixa_bp,
            "receita_realizada": receita_realizada,
            "despesa_empenhada": despesa_empenhada,
            "superavit_orcamentario": superavit_orcamentario,
            "superavit_patrimonial": superavit_patrimonial,
            "superavit_financeiro": superavit_financeiro,
        }
    except Exception as e:
        return {"erro": "falha", "mensagem": str(e)}'''

if matches_api:
    codigo = codigo[:matches_api[0].start()] + nova_funcao_api + codigo[matches_api[0].end():]
    for m in reversed(matches_api[1:]):
        codigo = codigo[:m.start()] + codigo[m.end():]

# =========================================================
# 2. LIMPAR E RECRIAR salvar_panorama
# =========================================================
padrao_salvar = re.compile(r'@app\.post\("/salvar_panorama/\{periodo\}"\).*?(?=\n@app\.|\n@app\.get|\Z)', re.DOTALL)
matches_salvar = list(padrao_salvar.finditer(codigo))

nova_funcao_salvar = '''@app.post("/salvar_panorama/{periodo}")
async def salvar_panorama(periodo: str):
    import sqlite3, json, os, datetime
    try:
        dados = await api_panorama(periodo)
        if dados.get("erro"):
            return {"erro": True, "mensagem": dados.get("mensagem", "Erro no calculo")}
            
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS historico_panorama (
            id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute("INSERT INTO historico_panorama (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                       (periodo, data_agora, json.dumps(dados, ensure_ascii=False)))
        conn.commit()
        conn.close()
        return {"ok": True, "mensagem": "Salvo com sucesso"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}'''

if matches_salvar:
    codigo = codigo[:matches_salvar[0].start()] + nova_funcao_salvar + codigo[matches_salvar[0].end():]
    for m in reversed(matches_salvar[1:]):
        codigo = codigo[:m.start()] + codigo[m.end():]

# =========================================================
# 3. LIMPAR E RECRIAR get_historico_panorama_id
# =========================================================
padrao_hist = re.compile(r'@app\.get\("/historico_panorama/\{id\}"\).*?(?=\n@app\.|\n@app\.get|\Z)', re.DOTALL)
matches_hist = list(padrao_hist.finditer(codigo))

nova_funcao_hist = '''@app.get("/historico_panorama/{id}")
async def get_historico_panorama_id(id: int):
    import sqlite3, json, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_panorama WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {"erro": "Historico nao encontrado"}
        
    return {
        "periodo": row[0],
        "data_geracao": row[1],
        "dados": json.loads(row[2])
    }'''

if matches_hist:
    codigo = codigo[:matches_hist[0].start()] + nova_funcao_hist + codigo[matches_hist[0].end():]
    for m in reversed(matches_hist[1:]):
        codigo = codigo[:m.start()] + codigo[m.end():]

with open(arquivo, "w", encoding="utf-8") as f:
    f.write(codigo)

print("\n[OK] Auditoria concluida: funcoes duplicadas removidas e substituidas pela versao correta.")
