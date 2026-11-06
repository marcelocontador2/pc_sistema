import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_dfc_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# 1. Importa o router da DFC
if "from app.routers import dfc" not in c:
    c = c.replace(
        "from app.routers import balanco_financeiro",
        "from app.routers import balanco_financeiro\nfrom app.routers import dfc"
    )
    if "from app.routers import balanco_financeiro" not in c:
        # Se nao achou, tenta adicionar no topo
        c = "from app.routers import dfc\n" + c

# 2. Registra o router da DFC
if "app.include_router(dfc.router)" not in c:
    c = c.replace(
        "app.include_router(balanco_financeiro.router)",
        "app.include_router(balanco_financeiro.router)\napp.include_router(dfc.router)"
    )
    if "app.include_router(balanco_financeiro.router)" not in c:
        # Se nao achou, procura por outro include
        c = c.replace(
            "app.include_router(",
            "app.include_router(dfc.router)\napp.include_router(",
            1
        )

# 3. Insere as rotas da DFC logo apos as rotas do BF
# (historico, get_bf_id, excluir, gerar_pdf, serve_analise_financeira_bf)
idx = c.find('@app.get("/analise_financeira_bf")')
if idx == -1:
    print("[ERRO] Rota /analise_financeira_bf nao encontrada.")
    exit(1)

fim_rota = c.find('@app', idx + 10)
if fim_rota == -1:
    fim_rota = len(c)

rotas_dfc = '''
# ============ ROTAS DFC (Analise do Fluxo de Caixa) ============

@app.post("/salvar_analise_dfc/{periodo_atual}/{periodo_anterior}")
async def salvar_analise_dfc(periodo_atual: str, periodo_anterior: str):
    import sqlite3, json
    from datetime import datetime
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS historico_analise_dfc (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    # Chama a API da DFC para obter os dados
    try:
        from app.routers.dfc import api_analise_dfc
        dados = await api_analise_dfc(periodo_atual)
    except Exception as e:
        return {"ok": False, "mensagem": f"Erro ao calcular DFC: {e}"}
    data_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO historico_analise_dfc (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                   (periodo_atual, data_agora, json.dumps(dados, ensure_ascii=False)))
    conn.commit()
    conn.close()
    return {"ok": True, "mensagem": "Analise DFC salva com sucesso!"}

@app.get("/historico_analise_dfc")
async def get_hist_dfc():
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS historico_analise_dfc (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    cursor.execute("SELECT id, periodo, data_geracao FROM historico_analise_dfc ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]

@app.get("/historico_analise_dfc/{id}")
async def get_dfc_id(id: int):
    import sqlite3, json
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_analise_dfc WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {"erro": "nao encontrado"}
    return {"periodo": row[0], "data_geracao": row[1], "dados": json.loads(row[2])}

@app.delete("/excluir_analise_dfc/{id}")
async def excluir_dfc(id: int):
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historico_analise_dfc WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/gerar_pdf_analise_dfc/{id}")
async def gerar_pdf_analise_dfc(id: int):
    # Placeholder: gera PDF simples com os dados
    import sqlite3, json, os
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    from fastapi.responses import Response
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_analise_dfc WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return Response(content="Historico nao encontrado.", status_code=404)
    periodo, data, res_json = row
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "COFEN/BR - Analise do Fluxo de Caixa (DFC)", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, f"Periodo: {periodo} | Gerado em: {data}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 6, "Dados salvos no banco. (PDF detalhado em construcao.)")
    pdf_bytes = bytes(pdf.output())
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=DFC_{periodo}.pdf"})

@app.get("/analise_dfc")
async def serve_analise_dfc():
    from fastapi.responses import FileResponse
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_dfc.html")
    return FileResponse(caminho, headers={"Cache-Control": "no-store, no-cache, must-revalidate", "Pragma": "no-cache"})

'''

c_novo = c[:fim_rota] + rotas_dfc + c[fim_rota:]
open(back_path, "w", encoding="utf-8").write(c_novo)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Rotas DFC inseridas no main.py e sintaxe validada!")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_dfc_{ts}", back_path)
    print("[OK] Backup restaurado.")
