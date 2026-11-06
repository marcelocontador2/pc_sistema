import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_pdf_just_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Localiza a rota do PDF de integridade
idx = c.find('@app.get("/gerar_pdf_integridade_matriz/{id}")')
if idx == -1:
    print("[ERRO] Rota do PDF de integridade nao encontrada.")
    exit(1)

# Encontra o final da funcao (proxima rota @app)
fim = c.find('@app', idx + 10)
if fim == -1:
    fim = len(c)

bloco_novo = '''@app.get("/gerar_pdf_integridade_matriz/{id}")
async def gerar_pdf_integridade_matriz(id: int):
    import sqlite3, json, os
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    from fastapi.responses import Response

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_integridade_matriz WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return Response(content="Historico nao encontrado.", status_code=404, media_type="text/plain")

    periodo, data_geracao, res_json = row
    try:
        dados = json.loads(res_json)
    except Exception:
        dados = {}

    matriz = dados.get("matriz", [])
    justificativas = dados.get("justificativas", {})

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "COFEN/BR - Matriz de Integridade", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, f"Periodo: {periodo} | Gerado em: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(5)

    # Cabecalhos da tabela
    colunas = ["NOMENCLATURA", "BALANCETE", "BP", "BF", "BO", "DFC", "DVP", "DMPL", "CONFERENCIA"]
    larguras = [60, 25, 25, 25, 25, 25, 25, 25, 25]

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(0, 86, 179)
    pdf.set_text_color(255, 255, 255)
    for i, col in enumerate(colunas):
        pdf.cell(larguras[i], 8, col, border=1, align="C", fill=True)
    pdf.ln()

    # Linhas da tabela
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 7)
    for r in matriz:
        pdf.cell(larguras[0], 6, str(r.get("item", ""))[:40], border=1, align="L")
        pdf.cell(larguras[1], 6, str(r.get("balancete", "")), border=1, align="R")
        pdf.cell(larguras[2], 6, str(r.get("bp", "")), border=1, align="R")
        pdf.cell(larguras[3], 6, str(r.get("bf", "")), border=1, align="R")
        pdf.cell(larguras[4], 6, str(r.get("bo", "")), border=1, align="R")
        pdf.cell(larguras[5], 6, str(r.get("dfc", "")), border=1, align="R")
        pdf.cell(larguras[6], 6, str(r.get("dvp", "")), border=1, align="R")
        pdf.cell(larguras[7], 6, str(r.get("dmpl", "")), border=1, align="R")
        pdf.cell(larguras[8], 6, str(r.get("conf", "")), border=1, align="C")
        pdf.ln()

    # Notas explicativas (apenas se houver)
    if justificativas:
        pdf.ln(10)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 8, "Notas Explicativas / Justificativas", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 9)
        for item, texto in justificativas.items():
            if texto.strip():
                pdf.multi_cell(0, 6, f"- {item}: {texto}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(2)

    pdf_bytes = bytes(pdf.output())
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=Integridade_{periodo}.pdf"})
'''

c_novo = c[:idx] + bloco_novo + c[fim:]
open(back_path, "w", encoding="utf-8").write(c_novo)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Rota do PDF alterada com sucesso e sintaxe validada!")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_pdf_just_{ts}", back_path)
    print("[OK] Backup restaurado.")
