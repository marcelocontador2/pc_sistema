import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_pdf_bf_total_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Localiza a rota do PDF do BF
idx = c.find('@app.get("/gerar_pdf_analise_financeira_bf/{id}")')
if idx == -1:
    print("[ERRO] Rota do PDF do BF nao encontrada.")
    exit(1)

# Encontra o final da rota (proxima @app)
fim = c.find('@app', idx + 10)
if fim == -1:
    fim = len(c)

novo_bloco = '''@app.get("/gerar_pdf_analise_financeira_bf/{id}")
async def gerar_pdf_analise_financeira_bf(id: int):
    try:
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        from fastapi.responses import Response
        from app.routers.balanco_financeiro import processar_bf
        import sqlite3, os
        from datetime import datetime

        fonte_padrao = "Helvetica"  # Definicao da fonte

        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT periodo FROM historico_analise_financeira_bf WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        periodo = row[0] if row else "2026-TRIMESTRE-3"

        periodo_atual = periodo.split(" vs ")[0].strip() if " vs " in periodo else periodo
        p_limpo = periodo_atual.replace("-", "_")
        caminho_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw", f"BALANCO_FINANCEIRO_{p_limpo}.csv")
        
        if not os.path.exists(caminho_csv):
            raise Exception(f"Arquivo do Balanco Financeiro nao encontrado para {periodo}")

        resultado = processar_bf(caminho_csv)
        d = resultado["dados"]

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=False)

        # Cabecalho
        pdf.set_fill_color(0, 51, 102)
        pdf.rect(0, 0, 210, 35, "F")
        pdf.set_font(fonte_padrao, "B", 22)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(15, 8)
        pdf.cell(180, 10, "Balanco Financeiro", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font(fonte_padrao, "", 13)
        pdf.set_xy(15, 20)
        pdf.cell(180, 8, f"Periodo: {periodo}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(1.5)
        pdf.line(0, 35, 210, 35)

        def fmt(v):
            try:
                s = f"R$ {v:,.2f}"
                return s.replace(",", "X").replace(".", ",").replace("X", ".")
            except Exception:
                return str(v)

        # --- CARDS DE TOTAIS ---
        y_pos = 50
        card_w = 55
        card_h = 25

        pdf.set_fill_color(232, 244, 248)
        pdf.rect(15, y_pos, card_w, card_h, "F")
        pdf.set_text_color(0, 51, 102)
        pdf.set_font(fonte_padrao, "B", 12)
        pdf.set_xy(18, y_pos + 4)
        pdf.cell(card_w - 6, 8, fmt(d["receitas"]["total"]["atual"]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font(fonte_padrao, "", 9)
        pdf.set_text_color(80, 80, 80)
        pdf.set_xy(18, y_pos + 15)
        pdf.cell(card_w - 6, 5, "Total de Receitas", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_fill_color(248, 232, 232)
        pdf.rect(77, y_pos, card_w, card_h, "F")
        pdf.set_text_color(220, 53, 69)
        pdf.set_font(fonte_padrao, "B", 12)
        pdf.set_xy(80, y_pos + 4)
        pdf.cell(card_w - 6, 8, fmt(d["despesas"]["total"]["atual"]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font(fonte_padrao, "", 9)
        pdf.set_text_color(80, 80, 80)
        pdf.set_xy(80, y_pos + 15)
        pdf.cell(card_w - 6, 5, "Total de Despesas", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_fill_color(238, 245, 232)
        pdf.rect(139, y_pos, card_w, card_h, "F")
        pdf.set_text_color(40, 167, 69)
        pdf.set_font(fonte_padrao, "B", 12)
        pdf.set_xy(142, y_pos + 4)
        pdf.cell(card_w - 6, 8, fmt(d["caixa"]["saldo_seguinte"]["atual"]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font(fonte_padrao, "", 9)
        pdf.set_text_color(80, 80, 80)
        pdf.set_xy(142, y_pos + 15)
        pdf.cell(card_w - 6, 5, "Saldo p/ Exerc. Seguinte", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # --- TABELA DETALHADA ---
        y_pos += 40
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(fonte_padrao, "B", 10)
        pdf.set_fill_color(0, 51, 102)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(15, y_pos)
        pdf.cell(90, 8, "Indicador", border=1, fill=True)
        pdf.cell(40, 8, "Periodo Atual", border=1, fill=True, align="R")
        pdf.cell(40, 8, "Periodo Anterior", border=1, fill=True, align="R")
        pdf.ln()
        y_pos += 8

        pdf.set_text_color(0, 0, 0)
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.2)
        pdf.set_font(fonte_padrao, "", 9)

        def add_linha(nome, at, ant, bold=False, fill_color=None, text_color=(0,0,0)):
            nonlocal y_pos
            if bold:
                pdf.set_font(fonte_padrao, "B", 9)
            else:
                pdf.set_font(fonte_padrao, "", 9)
            if fill_color:
                pdf.set_fill_color(*fill_color)
            pdf.set_text_color(*text_color)
            
            pdf.set_xy(15, y_pos)
            pdf.cell(90, 7, nome, border=1, fill=bool(fill_color))
            pdf.cell(40, 7, fmt(at), border=1, align="R", fill=bool(fill_color))
            pdf.cell(40, 7, fmt(ant), border=1, align="R", fill=bool(fill_color))
            pdf.ln()
            y_pos += 7

        # Grupo Receitas
        pdf.set_fill_color(232, 244, 248)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(fonte_padrao, "B", 9)
        pdf.set_xy(15, y_pos)
        pdf.cell(170, 7, "RECEITAS", border=1, fill=True)
        pdf.ln()
        y_pos += 7
        add_linha("Receitas Correntes", d["receitas"]["corrente"]["atual"], d["receitas"]["corrente"]["anterior"])
        add_linha("Receitas de Capital", d["receitas"]["capital"]["atual"], d["receitas"]["capital"]["anterior"])
        add_linha("TOTAL DE RECEITAS", d["receitas"]["total"]["atual"], d["receitas"]["total"]["anterior"], bold=True)

        # Grupo Despesas
        pdf.set_fill_color(248, 232, 232)
        pdf.set_font(fonte_padrao, "B", 9)
        pdf.set_xy(15, y_pos)
        pdf.cell(170, 7, "DESPESAS", border=1, fill=True)
        pdf.ln()
        y_pos += 7
        add_linha("Despesas Correntes", d["despesas"]["corrente"]["atual"], d["despesas"]["corrente"]["anterior"])
        add_linha("Despesas de Capital", d["despesas"]["capital"]["atual"], d["despesas"]["capital"]["anterior"])
        add_linha("TOTAL DE DESPESAS", d["despesas"]["total"]["atual"], d["despesas"]["total"]["anterior"], bold=True)

        # Grupo Extraorcamentario
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font(fonte_padrao, "B", 9)
        pdf.set_xy(15, y_pos)
        pdf.cell(170, 7, "EXTRAORCAMENTARIO", border=1, fill=True)
        pdf.ln()
        y_pos += 7
        add_linha("Recebimentos Extraorcamentarios", d["extra"]["recebimentos"]["atual"], d["extra"]["recebimentos"]["anterior"])
        add_linha("Pagamentos Extraorcamentarios", d["extra"]["pagamentos"]["atual"], d["extra"]["pagamentos"]["anterior"])

        # Grupo Caixa
        pdf.set_fill_color(238, 245, 232)
        pdf.set_font(fonte_padrao, "B", 9)
        pdf.set_xy(15, y_pos)
        pdf.cell(170, 7, "CAIXA E EQUIVALENTES", border=1, fill=True)
        pdf.ln()
        y_pos += 7
        add_linha("Saldo em Especie do Exercicio Anterior", d["caixa"]["saldo_anterior"]["atual"], d["caixa"]["saldo_anterior"]["anterior"])
        add_linha("Geracao Liquida de Caixa", d["caixa"]["geracao_liquida"]["atual"], d["caixa"]["geracao_liquida"]["anterior"], bold=True)
        add_linha("Saldo em Especie para o Exercicio Seguinte", d["caixa"]["saldo_seguinte"]["atual"], d["caixa"]["saldo_seguinte"]["anterior"], bold=True)

        # ==========================================
        # NOVOS TOTAIS (INGRESSOS E DISPENDIOS)
        # ==========================================
        y_pos += 10
        
        # Calculos de Ingressos
        totRecAt = d["receitas"]["total"]["atual"]
        totRecAnt = d["receitas"]["total"]["anterior"]
        totExtAt = d["extra"]["recebimentos"]["atual"]
        totExtAnt = d["extra"]["recebimentos"]["anterior"]
        saldoAntAt = d["caixa"]["saldo_anterior"]["atual"]
        saldoAntAnt = d["caixa"]["saldo_anterior"]["anterior"]

        totalIngAt = totRecAt + totExtAt + saldoAntAt
        totalIngAnt = totRecAnt + totExtAnt + saldoAntAnt

        # Tabela de Ingressos
        pdf.set_fill_color(0, 86, 179)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font(fonte_padrao, "B", 10)
        pdf.set_xy(15, y_pos)
        pdf.cell(170, 7, "TOTAL GERAL DE INGRESSOS", border=1, fill=True)
        pdf.ln()
        y_pos += 7
        
        add_linha("Receitas Orcamentarias (Corrente + Capital)", totRecAt, totRecAnt)
        add_linha("Recebimentos Extraorcamentarios", totExtAt, totExtAnt)
        add_linha("Saldo em Especie do Exercicio Anterior", saldoAntAt, saldoAntAnt)
        add_linha("TOTAL DE INGRESSOS", totalIngAt, totalIngAnt, bold=True, fill_color=(233, 236, 239), text_color=(0, 86, 179))

        # Calculos de Dispêndios
        y_pos += 10
        totDespAt = d["despesas"]["total"]["atual"]
        totDespAnt = d["despesas"]["total"]["anterior"]
        pagExtAt = d["extra"]["pagamentos"]["atual"]
        pagExtAnt = d["extra"]["pagamentos"]["anterior"]
        saldoSegAt = d["caixa"]["saldo_seguinte"]["atual"]
        saldoSegAnt = d["caixa"]["saldo_seguinte"]["anterior"]

        totalDispAt = totDespAt + pagExtAt + saldoSegAt
        totalDispAnt = totDespAnt + pagExtAnt + saldoSegAnt

        # Tabela de Dispêndios
        pdf.set_fill_color(220, 53, 69)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font(fonte_padrao, "B", 10)
        pdf.set_xy(15, y_pos)
        pdf.cell(170, 7, "TOTAL GERAL DE DISPENDIOS", border=1, fill=True)
        pdf.ln()
        y_pos += 7

        add_linha("Despesas Orcamentarias (Corrente + Capital)", totDespAt, totDespAnt)
        add_linha("Pagamentos Extraorcamentarios", pagExtAt, pagExtAnt)
        add_linha("Saldo em Especie para o Exercicio Seguinte", saldoSegAt, saldoSegAnt)
        add_linha("TOTAL DE DISPENDIOS", totalDispAt, totalDispAnt, bold=True, fill_color=(233, 236, 239), text_color=(220, 53, 69))

        # Rodape
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.3)
        pdf.line(15, 285, 195, 285)
        pdf.set_text_color(120, 120, 120)
        pdf.set_font(fonte_padrao, "I", 8)
        pdf.set_xy(15, 287)
        pdf.cell(90, 5, "Cofen - Analise das Demonstracoes Contabeis", new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_xy(135, 287)
        pdf.cell(60, 5, f"Gerado em: {datetime.now():%d/%m/%Y %H:%M}", align="R")

        pdf_bytes = bytes(pdf.output())
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=balanco_financeiro_{periodo}.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {str(e)}")

'''

c_novo = c[:idx] + novo_bloco + c[fim:]
open(back_path, "w", encoding="utf-8").write(c_novo)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Rota do PDF do BF atualizada com sucesso e sintaxe validada!")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_pdf_bf_total_{ts}", back_path)
    print("[OK] Backup restaurado.")
