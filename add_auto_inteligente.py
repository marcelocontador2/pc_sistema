p = 'pc_backend/main.py'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

# Localiza o bloco antigo da rota gerar_auto e substitui inteiro
import re
padrao = re.compile(r'@app\.post\("/api/notas_mcasp/gerar_auto"\).*?return \{"ok": True, "mensagem": "Rascunho gerado com sucesso!"\}', re.DOTALL)

nova_rota = '''@app.post("/api/notas_mcasp/gerar_auto")
async def api_gerar_auto_mcasp(request: Request):
    import sqlite3, os, json
    body = await request.json()
    periodo = body.get("periodo", "2026-TRIMESTRE-3")
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    def brl(v):
        if v is None: return "R$ 0,00"
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    # 1. Le Balanco Patrimonial
    cur.execute("SELECT resultado_json FROM historico_analise_bp WHERE periodo = ? ORDER BY id DESC LIMIT 1", (periodo,))
    row_bp = cur.fetchone()
    bp = json.loads(row_bp[0]).get('dados', {}) if row_bp else {}
    
    # 2. Le Balanco Orcamentario
    cur.execute("SELECT resultado_json FROM historico_analise_orcamentaria WHERE periodo_atual = ? ORDER BY id DESC LIMIT 1", (periodo,))
    row_bo = cur.fetchone()
    bo = json.loads(row_bo[0]).get('atual', {}) if row_bo else {}
    
    # 3. Le DFC
    cur.execute("SELECT resultado_json FROM historico_analise_dfc WHERE periodo = ? ORDER BY id DESC LIMIT 1", (periodo,))
    row_dfc = cur.fetchone()
    dfc = json.loads(row_dfc[0]).get('dados', {}) if row_dfc else {}
    
    # Monta os textos
    t_bp = f"O Ativo Circulante totalizou {brl(bp.get('ativo_circulante', {}).get('atual'))}, sendo composto principalmente por Caixa ({brl(bp.get('caixa', {}).get('atual'))}) e Creditos a Curto Prazo ({brl(bp.get('creditos', {}).get('atual'))}). O Ativo Nao Circulante somou {brl(bp.get('ativo_nao_circulante', {}).get('atual'))}."
    
    t_bo = f"A Receita Realizada no periodo foi de {brl(bo.get('receita_realizada'))}, enquanto a Despesa Empenhada atingiu {brl(bo.get('despesa_empenhada'))}. O Resultado Orcamentario apresentou um {'superavit' if bo.get('superavit', 0) >= 0 else 'deficit'} de {brl(abs(bo.get('superavit', 0)))}."
    
    t_dfc = f"As atividades operacionais geraram um fluxo liquido de caixa positivo de {brl(dfc.get('operacional', {}).get('liquido', {}).get('atual'))}."
    
    textos = {
        "3.1": "As demonstracoes contabeis foram elaboradas com base nos registros oficiais da entidade.",
        "3.1.1": f"Os creditos a curto prazo totalizam {brl(bp.get('creditos', {}).get('atual'))}.",
        "3.1.2": f"O ativo nao circulante (imobilizado e intangivel) totaliza {brl(bp.get('ativo_nao_circulante', {}).get('atual'))}.",
        "3.3.1": t_bo,
        "3.3.3": t_bo,
        "3.5": t_dfc
    }
    
    try:
        for codigo, texto in textos.items():
            cur.execute("UPDATE notas_mcasp_modelo SET texto = ? WHERE codigo = ?", (texto, codigo))
        conn.commit()
        return {"ok": True, "mensagem": "Rascunho gerado com dados reais!"}
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
    print('OK: Rota gerar_auto inteligente injetada com sucesso!')
