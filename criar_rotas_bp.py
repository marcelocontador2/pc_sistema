import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_bp_rotas_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Remove qualquer rota BP antiga (para recriar limpo)
c = re.sub(r'@app\.get\("/api/analise_bp/.*?(?=@app\.|if __name__)', '', c, flags=re.DOTALL)
c = re.sub(r'@app\.get\("/analise_bp"\).*?(?=@app\.|if __name__)', '', c, flags=re.DOTALL)

bloco_bp = '''

# ============================================================
# API E ROTAS DA ANALISE BP (Balanco Patrimonial)
# ============================================================

@app.get("/api/analise_bp/{periodo}")
async def api_analise_bp(periodo: str):
    import csv, os
    from fastapi import HTTPException
    
    p_limpo = periodo.replace("-", "_")
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    caminho = os.path.join(pasta, f"BALANCO_PATRIMONIAL_{p_limpo}.csv")
    
    if not os.path.exists(caminho):
        return {"erro": "faltando", "pecas": ["Balanco Patrimonial"]}
    
    def limpar(v):
        if not v:
            return 0.0
        v = str(v).replace("R$", "").strip()
        if v in ["-", "0,00", ""]:
            return 0.0
        if "," in v and "." in v:
            v = v.replace(".", "").replace(",", ".")
        elif "," in v:
            v = v.replace(",", ".")
        try:
            return float(v)
        except Exception:
            return 0.0
    
    try:
        linhas = []
        with open(caminho, "r", encoding="latin-1", errors="ignore") as f:
            leitor = csv.reader(f, delimiter=";")
            for row in leitor:
                linhas.append(row)
        
        def buscar(termo):
            termo = termo.upper().strip()
            for p in linhas:
                if len(p) > 2 and termo in str(p[0]).upper():
                    return limpar(p[1]), limpar(p[2])
                if len(p) > 4 and termo in str(p[3]).upper():
                    return limpar(p[4]), limpar(p[5])
            return 0.0, 0.0
        
        dados = {
            "ativo_circulante": buscar("ATIVO CIRCULANTE"),
            "caixa": buscar("CAIXA E EQUIVALENTES"),
            "creditos": buscar("CREDITOS A CURTO PRAZO"),
            "ativo_nao_circulante": buscar("ATIVO NAO CIRCULANTE"),
            "imobilizado": buscar("IMOBILIZADO"),
            "passivo_circulante": buscar("PASSIVO CIRCULANTE"),
            "passivo_nao_circulante": buscar("PASSIVO NAO CIRCULANTE"),
            "patrimonio_liquido": buscar("PATRIMONIO LIQUIDO"),
        }
        
        resultado = {}
        for k, (v_at, v_ant) in dados.items():
            resultado[k] = {"atual": v_at, "anterior": v_ant}
        
        return {"erro": False, "dados": resultado}
    
    except Exception as e:
        print(f"[BP] ERRO: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analise_bp")
async def serve_analise_bp():
    from fastapi.responses import FileResponse
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_bp.html")
    return FileResponse(caminho, headers={"Cache-Control": "no-store, no-cache, must-revalidate"})

@app.post("/salvar_analise_bp/{periodo}")
async def salvar_analise_bp(periodo: str):
    import sqlite3, json, os
    from datetime import datetime
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS historico_analise_bp (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    
    # Chama a API para pegar os dados atuais
    try:
        dados = await api_analise_bp(periodo)
    except Exception as e:
        return {"ok": False, "mensagem": f"Erro ao calcular BP: {e}"}
    
    data_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO historico_analise_bp (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                   (periodo, data_agora, json.dumps(dados, ensure_ascii=False)))
    conn.commit()
    conn.close()
    return {"ok": True, "mensagem": "Analise BP salva com sucesso!"}

@app.get("/historico_analise_bp")
async def get_hist_bp():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS historico_analise_bp (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    cursor.execute("SELECT id, periodo, data_geracao FROM historico_analise_bp ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]

@app.get("/historico_analise_bp/{id}")
async def get_bp_id(id: int):
    import sqlite3, json, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_analise_bp WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {"erro": "nao encontrado"}
    return {"periodo": row[0], "data_geracao": row[1], "dados": json.loads(row[2])}

@app.delete("/excluir_analise_bp/{id}")
async def excluir_bp(id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historico_analise_bp WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/gerar_pdf_analise_bp/{id}")
async def gerar_pdf_analise_bp(id: int):
    import sqlite3, json, os
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    from fastapi.responses import Response
    from datetime import datetime
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_analise_bp WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return Response(content="Historico nao encontrado.", status_code=404)
    
    periodo, data_geracao, res_json = row
    try:
        dados = json.loads(res_json)
    except Exception:
        dados = {}
    
    d = dados.get("dados", {})
    
    def fmt(v):
        if v is None: return "0,00"
        return f"{(v/1000000):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    
    pdf.set_fill_color(0, 51, 102)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 15, "COFEN/BR - ANALISE DO BALANCO PATRIMONIAL", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(5)
    pdf.cell(0, 6, f"Periodo: {periodo} | Gerado em: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)
    
    # Tabela
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(0, 86, 179)
    pdf.set_text_color(255, 255, 255)
    col_w = [70, 40, 40, 30]
    headers = ["Conta", "2025 (R$ mi)", "2026 (R$ mi)", "Var. (%)"]
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 8, h, border=1, align="C", fill=True)
    pdf.ln()
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 8)
    
    def linha(label, va, vb):
        pdf.cell(col_w[0], 7, label, border=1, align="L")
        pdf.cell(col_w[1], 7, fmt(vb), border=1, align="R")
        pdf.cell(col_w[2], 7, fmt(va), border=1, align="R")
        pct = "-" if not vb else f"{(((va - vb) / abs(vb)) * 100):,.2f}%".replace(".", ",")
        pdf.cell(col_w[3], 7, pct, border=1, align="R")
        pdf.ln()
    
    linha("Ativo Circulante", d.get("ativo_circulante", {}).get("atual", 0), d.get("ativo_circulante", {}).get("anterior", 0))
    linha("Caixa e Equivalentes", d.get("caixa", {}).get("atual", 0), d.get("caixa", {}).get("anterior", 0))
    linha("Creditos a Curto Prazo", d.get("creditos", {}).get("atual", 0), d.get("creditos", {}).get("anterior", 0))
    linha("Ativo Nao Circulante", d.get("ativo_nao_circulante", {}).get("atual", 0), d.get("ativo_nao_circulante", {}).get("anterior", 0))
    linha("Imobilizado", d.get("imobilizado", {}).get("atual", 0), d.get("imobilizado", {}).get("anterior", 0))
    linha("Passivo Circulante", d.get("passivo_circulante", {}).get("atual", 0), d.get("passivo_circulante", {}).get("anterior", 0))
    linha("Passivo Nao Circulante", d.get("passivo_nao_circulante", {}).get("atual", 0), d.get("passivo_nao_circulante", {}).get("anterior", 0))
    linha("Patrimonio Liquido", d.get("patrimonio_liquido", {}).get("atual", 0), d.get("patrimonio_liquido", {}).get("anterior", 0))
    
    pdf_bytes = bytes(pdf.output())
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=Analise_BP_{periodo}.pdf"})

'''

# Insere antes do if __name__
idx = c.find("if __name__")
if idx == -1:
    idx = len(c)
c = c[:idx] + bloco_bp + c[idx:]
open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Rotas da Analise BP (API, Historico, Salvar, Excluir, PDF) criadas.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_bp_rotas_{ts}", back_path)
