arq = r"pc_backend\main.py"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

# 1. O bloco antigo (que puxa direto do JSON)
bloco_antigo = """        ind = [
            ("Receita Realizada", "receita_realizada", 1e6),
            ("Despesas Empenhadas", "despesa_empenhada", 1e6),
            ("Superavit Orcamentario", "superavit", 1e6),
            ("Restos a Pagar Inscritos", "restos_pagar", 1e6),
            ("Receitas Orcadas", "receita_orcada", 1e6),
            ("Despesas Orcadas", "despesa_orcada", 1e6),
            ("% de Realizacao das Receitas", "pct_receita", 1),
            ("% de Realizacao das Despesas", "pct_despesa", 1),
        ]
        for nome, chave, m in ind:
            va = a.get(chave, 0)
            vb = b.get(chave, 0)
            var = ((va - vb) / abs(vb)) * 100 if vb != 0 else 0
            pdf.cell(80, 7, nome, border=1, align="L")
            pdf.cell(45, 7, fmt(va) if m == 1e6 else f"{va:.2f}%", border=1, align="R")
            pdf.cell(45, 7, fmt(vb) if m == 1e6 else f"{vb:.2f}%", border=1, align="R")
            if var >= 0: pdf.set_text_color(0, 128, 0)
            else: pdf.set_text_color(220, 53, 69)
            pdf.cell(30, 7, f"{var:+.2f}%".replace(".", ","), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)"""

# 2. O novo bloco calcula os percentuais na hora para garantir que não fiquem zerados
bloco_novo = """        # Calcula os percentuais na hora para garantir precisão
        rec_orc = a.get("receita_orcada", 0) or 0
        rec_real = a.get("receita_realizada", 0) or 0
        desp_orc = a.get("despesa_orcada", 0) or 0
        desp_emp = a.get("despesa_empenhada", 0) or 0
        
        rec_orc_ant = b.get("receita_orcada", 0) or 0
        rec_real_ant = b.get("receita_realizada", 0) or 0
        desp_orc_ant = b.get("despesa_orcada", 0) or 0
        desp_emp_ant = b.get("despesa_empenhada", 0) or 0

        pct_rec = (rec_real / rec_orc * 100) if rec_orc else 0
        pct_desp = (desp_emp / desp_orc * 100) if desp_orc else 0
        
        pct_rec_ant = (rec_real_ant / rec_orc_ant * 100) if rec_orc_ant else 0
        pct_desp_ant = (desp_emp_ant / desp_orc_ant * 100) if desp_orc_ant else 0

        ind = [
            ("Receita Realizada", rec_real, rec_real_ant, 1e6),
            ("Despesas Empenhadas", desp_emp, desp_emp_ant, 1e6),
            ("Superavit Orcamentario", a.get("superavit", 0), b.get("superavit", 0), 1e6),
            ("Restos a Pagar Inscritos", a.get("restos_pagar", 0), b.get("restos_pagar", 0), 1e6),
            ("Receitas Orcadas", rec_orc, rec_orc_ant, 1e6),
            ("Despesas Orcadas", desp_orc, desp_orc_ant, 1e6),
            ("% de Realizacao das Receitas", pct_rec, pct_rec_ant, 1),
            ("% de Realizacao das Despesas", pct_desp, pct_desp_ant, 1),
        ]
        
        for nome, va, vb, m in ind:
            var = ((va - vb) / abs(vb)) * 100 if vb != 0 else 0
            pdf.cell(80, 7, nome, border=1, align="L")
            pdf.cell(45, 7, fmt(va) if m == 1e6 else f"{va:.2f}%", border=1, align="R")
            pdf.cell(45, 7, fmt(vb) if m == 1e6 else f"{vb:.2f}%", border=1, align="R")
            if var >= 0: pdf.set_text_color(0, 128, 0)
            else: pdf.set_text_color(220, 53, 69)
            pdf.cell(30, 7, f"{var:+.2f}%".replace(".", ","), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)"""

html = html.replace(bloco_antigo, bloco_novo)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Percentuais de Análise Orçamentária calculados e injetados no PDF do BO!")
