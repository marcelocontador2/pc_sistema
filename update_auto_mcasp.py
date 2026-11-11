p = 'pc_backend/main.py'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

import re
padrao = re.compile(r'@app\.post\("/api/notas_mcasp/gerar_auto"\).*?return \{"ok": True, "mensagem": "Rascunho gerado com dados reais!"\}', re.DOTALL)

nova_rota = '''@app.post("/api/notas_mcasp/gerar_auto")
async def api_gerar_auto_mcasp(request: Request):
    import sqlite3, os, json
    body = await request.json()
    periodo = body.get("periodo", "2026-TRIMESTRE-3")
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    def brl(v):
        if v is None or v == 0: return "R$ 0,00"
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    textos = {}
    
    # 1. Balanco Patrimonial
    try:
        cur.execute("SELECT resultado_json FROM historico_analise_bp WHERE periodo = ? ORDER BY id DESC LIMIT 1", (periodo,))
        r = cur.fetchone()
        if r:
            bp = json.loads(r[0]).get('dados', {})
            caixa = bp.get('caixa', {}).get('atual', 0)
            creditos = bp.get('creditos', {}).get('atual', 0)
            nao_circ = bp.get('ativo_nao_circulante', {}).get('atual', 0)
            ativo_circ = bp.get('ativo_circulante', {}).get('atual', 0)
            
            textos["3.1"] = f"O Ativo Total da entidade apresentou a composição patrimonial detalhada a seguir, refletindo a posição financeira no encerramento do período."
            textos["3.1.1"] = f"Os créditos a curto prazo totalizaram {brl(creditos)}, representando os valores a receber pela entidade."
            textos["3.1.2"] = f"O Ativo Não Circulante, composto por Imobilizado e Intangível, totalizou {brl(nao_circ)}."
            textos["3.1.7"] = f"As disponibilidades (Caixa e Equivalentes) encerraram o período com saldo de {brl(caixa)}, enquanto o Ativo Circulante total somou {brl(ativo_circ)}."
    except Exception: pass
    
    # 2. Balanco Orcamentario
    try:
        cur.execute("SELECT resultado_json FROM historico_analise_orcamentaria WHERE periodo_atual = ? ORDER BY id DESC LIMIT 1", (periodo,))
        r = cur.fetchone()
        if r:
            bo = json.loads(r[0]).get('atual', {})
            rec = bo.get('receita_realizada', 0)
            desp = bo.get('despesa_empenhada', 0)
            sup = bo.get('superavit', 0)
            status = "superávit" if sup >= 0 else "déficit"
            
            textos["3.3"] = f"O Balanço Orçamentário demonstra a execução das receitas e despesas autorizadas na LOA."
            textos["3.3.1"] = f"A Receita Realizada no período foi de {brl(rec)}, enquanto a Despesa Empenhada atingiu {brl(desp)}."
            textos["3.3.3"] = f"As despesas foram executadas majoritariamente por créditos iniciais, totalizando {brl(desp)}."
            textos["3.3.4"] = f"O Resultado Orçamentário apurado apresentou um {status} de {brl(abs(sup))}."
    except Exception: pass
    
    # 3. DFC
    try:
        cur.execute("SELECT resultado_json FROM historico_analise_dfc WHERE periodo = ? ORDER BY id DESC LIMIT 1", (periodo,))
        r = cur.fetchone()
        if r:
            dfc = json.loads(r[0]).get('dados', {})
            op = dfc.get('operacional', {}).get('liquido', {}).get('atual', 0)
            inv = dfc.get('investimento', {}).get('liquido', {}).get('atual', 0)
            fin = dfc.get('financiamento', {}).get('liquido', {}).get('atual', 0)
            
            textos["3.5"] = f"As atividades operacionais geraram um fluxo líquido de {brl(op)}. As atividades de investimento resultaram em {brl(inv)} e as de financiamento em {brl(fin)}."
            textos["3.5.1"] = f"Os saldos de caixa e equivalentes estão disponíveis para uso imediato, garantindo a liquidez da entidade."
    except Exception: pass
    
    # 4. DMPL
    try:
        cur.execute("SELECT resultado_json FROM historico_analise_dmpl WHERE periodo = ? ORDER BY id DESC LIMIT 1", (periodo,))
        r = cur.fetchone()
        if r:
            textos["3.6"] = "A Demonstração das Mutações do Patrimônio Líquido evidencia as alterações ocorridas no patrimônio social e nos resultados acumulados durante o período."
    except Exception: pass

    # Textos fixos / padrão para itens sem dados numéricos
    textos["1.1"] = "O Conselho Federal de Enfermagem (COFEN) é uma autarquia federal, com sede em Brasília/DF, responsável pela normatização e fiscalização da profissão."
    textos["1.2"] = "As demonstrações contábeis foram elaboradas em conformidade com a Lei nº 4.320/1964, as diretrizes do MCASP e as NBC TSP."
    textos["2.1"] = "As demonstrações são elaboradas com base no regime de competência (VPA/VPD) e regime de caixa (Fluxos de Caixa)."
    
    try:
        for codigo, texto in textos.items():
            cur.execute("UPDATE notas_mcasp_modelo SET texto = ? WHERE codigo = ?", (texto, codigo))
        conn.commit()
        return {"ok": True, "mensagem": f"Rascunho gerado com sucesso para o período {periodo}!"}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "mensagem": str(e)}
    finally:
        conn.close()
'''

if not padrao.search(s):
    print('ERRO: rota antiga nao encontrada.')
else:
    s = padrao.sub(nova_rota, s)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s)
    print('OK: Rota gerar_auto inteligente atualizada com todos os mapeamentos!')
