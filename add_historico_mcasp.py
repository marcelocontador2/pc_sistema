p = 'pc_backend/main.py'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

rotas_salvar = '''
@app.post("/api/notas_mcasp/salvar_historico")
async def api_salvar_historico_mcasp(request: Request):
    import sqlite3, os, json, datetime
    body = await request.json()
    periodo = body.get("periodo", "2026-TRIMESTRE-3")
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        # Pega os textos atuais do modelo MCASP
        cur.execute("SELECT codigo, titulo, texto FROM notas_mcasp_modelo WHERE texto != '' ORDER BY ordem")
        itens = [{"codigo": r[0], "titulo": r[1], "texto": r[2]} for r in cur.fetchall()]
        
        if not itens:
            return {"ok": False, "mensagem": "Nenhum texto preenchido para salvar."}
            
        # Empacota no formato JSON que o sistema entende
        resultado_json = json.dumps({"tipo": "mcasp", "notas": itens}, ensure_ascii=False)
        data_geracao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Salva na tabela de historico oficial
        cur.execute("INSERT INTO historico_notas_explicativas (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)", 
                    (periodo, data_geracao, resultado_json))
        conn.commit()
        return {"ok": True, "mensagem": "Historico do MCASP salvo com sucesso!"}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "mensagem": str(e)}
    finally:
        conn.close()
'''

anchor = '@app.get("/notas_mcasp")'
if '/api/notas_mcasp/salvar_historico' in s:
    print('AVISO: Rota ja existe')
else:
    s = s.replace(anchor, rotas_salvar + '\n' + anchor, 1)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s)
    print('OK: Rota de salvar historico MCASP injetada!')
