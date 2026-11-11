import io
p = 'pc_backend/main.py'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

# ---- 1) Inserir rotas CRUD antes de @app.get('/gerar_pdf_notas/{id}')
anchor = '@app.get(\"/gerar_pdf_notas/{id}\")'
rotas = '''@app.get(\"/api/declaracao_conformidade\")
async def listar_itens_declaracao():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), \"..\", \"pc_storage\", \"banco_dados.db\")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(\"SELECT id, ordem, texto, ativo FROM itens_declaracao_conformidade WHERE ativo = TRUE ORDER BY ordem, id\")
    rows = cur.fetchall()
    conn.close()
    return [{\"id\": r[0], \"ordem\": r[1], \"texto\": r[2], \"ativo\": r[3]} for r in rows]

@app.post(\"/api/declaracao_conformidade\")
async def incluir_item_declaracao(request: Request):
    import sqlite3, os
    body = await request.json()
    texto = (body.get(\"texto\") or \"\").strip()
    if not texto:
        return {\"ok\": False, \"mensagem\": \"Texto vazio\"}
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), \"..\", \"pc_storage\", \"banco_dados.db\")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(\"SELECT COALESCE(MAX(ordem), 0) + 1 FROM itens_declaracao_conformidade\")
    prox_ordem = cur.fetchone()[0]
    cur.execute(\"INSERT INTO itens_declaracao_conformidade (ordem, texto) VALUES (?, ?)\", (prox_ordem, texto))
    novo_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {\"ok\": True, \"id\": novo_id, \"ordem\": prox_ordem, \"texto\": texto}

@app.put(\"/api/declaracao_conformidade/{item_id}\")
async def editar_item_declaracao(item_id: int, request: Request):
    import sqlite3, os
    body = await request.json()
    texto = (body.get(\"texto\") or \"\").strip()
    if not texto:
        return {\"ok\": False, \"mensagem\": \"Texto vazio\"}
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), \"..\", \"pc_storage\", \"banco_dados.db\")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(\"UPDATE itens_declaracao_conformidade SET texto = ? WHERE id = ?\", (texto, item_id))
    conn.commit()
    conn.close()
    return {\"ok\": True}

@app.delete(\"/api/declaracao_conformidade/{item_id}\")
async def excluir_item_declaracao(item_id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), \"..\", \"pc_storage\", \"banco_dados.db\")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(\"DELETE FROM itens_declaracao_conformidade WHERE id = ?\", (item_id,))
    conn.commit()
    conn.close()
    return {\"ok\": True}

'''
if anchor not in s:
    print('ERRO: anchor /gerar_pdf_notas nao encontrado')
    raise SystemExit(1)
if '/api/declaracao_conformidade' in s:
    print('AVISO: rotas ja existem, pulando insercao')
else:
    s = s.replace(anchor, rotas + anchor, 1)
    print('OK: 4 rotas CRUD inseridas')

# ---- 2) Substituir o bloco hardcoded de 5 itens por loop dinamico
old_block = '''        '<p style=\"text-align: justify; line-height: 1.6; font-size: 13px; margin-bottom: 12px;\"><b>1.</b> As informa횄짠횄쨉es cont횄징beis foram elaboradas em conformidade com as disposi횄짠횄쨉es da Lei n횂쨘 4.320/1964, as diretrizes do MCASP e as NBC TSP.</p>'
        '<p style=\"text-align: justify; line-height: 1.6; font-size: 13px; margin-bottom: 12px;\"><b>2.</b> As demonstra횄짠횄쨉es cont횄징beis consolidadas refletem, de forma fidedigna, a posi횄짠횄짙o patrimonial e financeira do COFEN e o desempenho da execu횄짠횄짙o or횄짠ament횄징ria no per횄odo.</p>'
        '<p style=\"text-align: justify; line-height: 1.6; font-size: 13px; margin-bottom: 12px;\"><b>3.</b> Os registros cont횄징beis est횄짙o amparados em documenta횄짠횄짙o de suporte id횄쨈nea e devidamente auditada internamente.</p>'
        '<p style=\"text-align: justify; line-height: 1.6; font-size: 13px; margin-bottom: 12px;\"><b>4.</b> As pr횄징ticas de gest횄짙o de riscos e controles internos foram implementados e mantidos operantes durante todo o per횄odo analisado.</p>'
        '<p style=\"text-align: justify; line-height: 1.6; font-size: 13px; margin-bottom: 12px;\"><b>5.</b> Esta declara횄짠횄짙o 횄짤 firmada com base nas informa횄짠횄쨉es extra횄das dos sistemas corporativos e validadas pelos respons횄징veis t횄짤cnicos.</p>'
'''
new_block = '''        + html_itens_declaracao
'''
if old_block not in s:
    print('AVISO: bloco hardcoded nao encontrado, pulando substituicao')
else:
    s = s.replace(old_block, new_block, 1)
    print('OK: bloco hardcoded substituido por html_itens_declaracao')

# ---- 3) Inserir leitura dos itens + geracao do HTML antes do html_declaracao
anchor2 = '    html_declaracao = ('
leitura_itens = '''    # Le itens da declaracao do banco
    conn2 = sqlite3.connect(db_path)
    cur2 = conn2.cursor()
    cur2.execute(\"SELECT texto FROM itens_declaracao_conformidade WHERE ativo = TRUE ORDER BY ordem, id\")
    itens_decl = [r[0] for r in cur2.fetchall()]
    conn2.close()
    html_itens_declaracao = \"\"
    for i, txt in enumerate(itens_decl, start=1):
        html_itens_declaracao += '<p style=\"text-align: justify; line-height: 1.6; font-size: 13px; margin-bottom: 12px;\"><b>' + str(i) + '.</b> ' + txt + '</p>'

'''
if anchor2 not in s:
    print('ERRO: anchor html_declaracao nao encontrado')
    raise SystemExit(1)
if 'html_itens_declaracao = ' in s:
    print('AVISO: leitura de itens ja existe, pulando')
else:
    s = s.replace(anchor2, leitura_itens + anchor2, 1)
    print('OK: leitura de itens + geracao HTML inseridas')

with open(p, 'w', encoding='utf-8') as f:
    f.write(s)
print('main.py atualizado')
