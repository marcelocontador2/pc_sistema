import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_pdf_dfc_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Localiza a rota antiga do PDF da DFC
idx = c.find('@app.get("/gerar_pdf_analise_dfc/{id}")')
if idx == -1:
    print("[ERRO] Rota do PDF da DFC nao encontrada.")
    exit(1)

fim = c.find('@app', idx + 10)
if fim == -1:
    fim = len(c)

bloco_novo = '''@app.get("/gerar_pdf_analise_dfc/{id}")
async def gerar_pdf_analise_dfc(id: int):
    import sqlite3, json, os
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    from fastapi.responses import Response
    from datetime import datetime

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_analise_dfc WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return Response(content="Historico nao encontrado.", status_code=404, media_type="text/plain")

    periodo, data_geracao, res_json = row
    try:
        dados = json.loads(res_json)
    except Exception:
        dados = {}

    d = dados.get("dados", {})
    op = d.get("operacional", {})
    inv = d.get("investimento", {})
    fin = d.get("financiamento", {})
    cxa = d.get("caixa", {})

    def fmt(v):
        if v is None: return "0,00"
        return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def pct(va, vb):
        if not vb or vb == 0: return "0,00%"
        return f"{(((va - vb) / abs(vb)) * 100):,.2f}%".replace(".", ",")

    # Inicia o PDF
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    
    # Cabecalho
    pdf.set_fill_color(0, 51, 102)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 15, "COFEN/BR - ANALISE DA DEMONSTRACAO DO FLUXO DE CAIXA", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 10)
    pdf.ln(5)
    pdf.cell(0, 6, f"Periodo de Referencia: {periodo.replace('-', ' ')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 6, f"Data de Geracao do Relatorio: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)

    # Tabela
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(0, 86, 179)
    pdf.set_text_color(255, 255, 255)
    
    col_w = [70, 35, 35, 30]
    headers = ["ESPECIFICACAO", "PERIODO ATUAL", "PERIODO ANTERIOR", "VAR. (%)"]
    
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 8, h, border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 8)
    
    def draw_row(label, va, vb, is_header=False, is_total=False):
        if is_header:
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(sum(col_w), 6, label, border=1, align="L", fill=True)
            pdf.ln()
            return
        if is_total:
            pdf.set_font("Helvetica", "B", 8)
        else:
            pdf.set_font("Helvetica", "", 8)
            
        pdf.cell(col_w[0], 6, label, border=1, align="L")
        pdf.cell(col_w[1], 6, fmt(va), border=1, align="R")
        pdf.cell(col_w[2], 6, fmt(vb), border=1, align="R")
        v = pct(va, vb)
        pdf.cell(col_w[3], 6, v, border=1, align="R")
        pdf.ln()

    # Operacional
    draw_row("FLUXO DE CAIXA DAS ATIVIDADES DAS OPERACOES", 0, 0, is_header=True)
    draw_row("Ingressos Operacionais", op.get("ingressos", {}).get("atual", 0), op.get("ingressos", {}).get("anterior", 0))
    draw_row("Desembolsos Operacionais", op.get("desembolsos", {}).get("atual", 0), op.get("desembolsos", {}).get("anterior", 0))
    draw_row("Caixa Liquido das Operacoes", op.get("liquido", {}).get("atual", 0), op.get("liquido", {}).get("anterior", 0), is_total=True)
    
    # Investimento
    draw_row("FLUXO DE CAIXA DAS ATIVIDADES DE INVESTIMENTO", 0, 0, is_header=True)
    draw_row("Ingressos de Investimento", inv.get("ingressos", {}).get("atual", 0), inv.get("ingressos", {}).get("anterior", 0))
    draw_row("Desembolsos de Investimento", inv.get("desembolsos", {}).get("atual", 0), inv.get("desembolsos", {}).get("anterior", 0))
    draw_row("Caixa Liquido de Investimento", inv.get("liquido", {}).get("atual", 0), inv.get("liquido", {}).get("anterior", 0), is_total=True)
    
    # Financiamento
    draw_row("FLUXO DE CAIXA DAS ATIVIDADES DE FINANCIAMENTO", 0, 0, is_header=True)
    draw_row("Ingressos de Financiamento", fin.get("ingressos", {}).get("atual", 0), fin.get("ingressos", {}).get("anterior", 0))
    draw_row("Desembolsos de Financiamento", fin.get("desembolsos", {}).get("atual", 0), fin.get("desembolsos", {}).get("anterior", 0))
    draw_row("Caixa Liquido de Financiamento", fin.get("liquido", {}).get("atual", 0), fin.get("liquido", {}).get("anterior", 0), is_total=True)
    
    # Apuracao
    draw_row("APURACAO DO FLUXO DE CAIXA DO PERIODO", 0, 0, is_header=True)
    draw_row("Geracao Liquida de Caixa", cxa.get("geracao", {}).get("atual", 0), cxa.get("geracao", {}).get("anterior", 0), is_total=True)
    draw_row("Caixa e Equivalentes Inicial", cxa.get("inicial", {}).get("atual", 0), cxa.get("inicial", {}).get("anterior", 0))
    draw_row("Caixa e Equivalentes Final", cxa.get("final", {}).get("atual", 0), cxa.get("final", {}).get("anterior", 0), is_total=True)
    
    pdf.ln(10)

    # Analise Textual
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "1. ANALISE DAS ATIVIDADES OPERACIONAIS", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 9)
    
    liq_op = op.get("liquido", {}).get("atual", 0)
    if liq_op > 0:
        txt_op = f"As atividades operacionais geraram um caixa liquido positivo de R$ {fmt(liq_op)} no periodo atual. Isso indica que as receitas e ingressos operacionais foram suficientes para cobrir os custos e desembolsos operacionais."
    else:
        txt_op = f"As atividades operacionais apresentaram um caixa liquido negativo de R$ {fmt(liq_op)} no periodo atual. Isso demonstra que a entidade precisou consumir reservas ou obter financiamentos para cobrir seus desembolsos operacionais."
    
    pdf.multi_cell(0, 5, txt_op)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "2. ANALISE DAS ATIVIDADES DE INVESTIMENTO", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 9)
    
    liq_inv = inv.get("liquido", {}).get("atual", 0)
    if liq_inv < 0:
        txt_inv = f"O fluxo de caixa de investimentos foi negativo em R$ {fmt(abs(liq_inv))}, o que e comum e esperado quando a entidade realiza aquisicoes de ativos (investimentos) e imobilizacoes."
    else:
        txt_inv = f"O fluxo de caixa de investimentos foi positivo em R$ {fmt(liq_inv)}, indicando que a entidade obteve mais recursos com alienacao de ativos do que gastou com aquisicoes."
    
    pdf.multi_cell(0, 5, txt_inv)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "3. ANALISE DAS ATIVIDADES DE FINANCIAMENTO", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 9)
    
    liq_fin = fin.get("liquido", {}).get("atual", 0)
    if liq_fin > 0:
        txt_fin = f"O fluxo de caixa de financiamentos foi positivo em R$ {fmt(liq_fin)}, decorrente de captacao de emprestimos ou financiamentos."
    elif liq_fin < 0:
        txt_fin = f"O fluxo de caixa de financiamentos foi negativo em R$ {fmt(abs(liq_fin))}, indicando amortizacao de dividas ou devolucao de recursos."
    else:
        txt_fin = "Nao houve movimentacao significativa no fluxo de caixa de financiamentos no periodo."
        
    pdf.multi_cell(0, 5, txt_fin)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "4. CONCLUSAO SOBRE A LIQUIDEZ", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 9)
    
    geracao = cxa.get("geracao", {}).get("atual", 0)
    inicial = cxa.get("inicial", {}).get("atual", 0)
    final = cxa.get("final", {}).get("atual", 0)
    
    txt_concl = f"A entidade encerrou o periodo com um saldo de caixa de R$ {fmt(final)} (variacao de R$ {fmt(geracao)} em relacao ao saldo inicial de R$ {fmt(inicial)}). "
    if geracao > 0:
        txt_concl += "O aumento no saldo de caixa demonstra uma boa geracao de recursos no periodo."
    else:
        txt_concl += "A reducao no saldo de caixa requer atencao aos proximos periodos para garantir a manutencao das atividades."
        
    pdf.multi_cell(0, 5, txt_concl)

    pdf.ln(15)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(0, 5, "Relatorio gerado automaticamente pelo Sistema SIGPC/COFEN", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    pdf_bytes = bytes(pdf.output())
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=Analise_DFC_{periodo}.pdf"})
'''

c_novo = c[:idx] + bloco_novo + c[fim:]
open(back_path, "w", encoding="utf-8").write(c_novo)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Rota do PDF da DFC reescrita com sucesso e sintaxe validada!")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_pdf_dfc_{ts}", back_path)
    print("[OK] Backup restaurado.")
