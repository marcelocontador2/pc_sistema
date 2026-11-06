import re, shutil, datetime

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_pdf_premium_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

# Remove a rota antiga do PDF consolidado
padrao_antigo = re.compile(
    r'@app\.get\("/gerar_pdf_relatorio_consolidado/\{id\}"\).*?(?=\n@app\.|\Z)',
    re.DOTALL
)
main_code = padrao_antigo.sub("", main_code)

# Adiciona a nova rota de alto padrão
nova_rota = '''
@app.get("/gerar_pdf_relatorio_consolidado/{id}")
async def gerar_pdf_relatorio_consolidado(id: int):
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    from fastapi.responses import Response
    import sqlite3, json, os

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_relatorio_consolidado WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return Response(content="Histórico não encontrado.", status_code=404, media_type="text/plain")

    periodo, data_geracao, resultado_json = row
    dados = json.loads(resultado_json)
    modulos = dados.get("dados", {})

    # ============ UTILITÁRIOS ============
    AZUL = (0, 51, 102)
    AZUL_CLARO = (0, 86, 179)
    CINZA_CLARO = (245, 247, 250)
    CINZA_LINHA = (230, 230, 230)
    VERDE = (39, 174, 96)
    VERMELHO = (192, 57, 43)

    def fmt_moeda(v):
        if v is None: return "R$ 0,00"
        try:
            v = float(v)
            if abs(v) >= 1_000_000:
                return f"R$ {v/1_000_000:,.1f} mi".replace(",", "X").replace(".", ",").replace("X", ".")
            return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return str(v)

    def fmt_pct(v):
        if v is None: return "0,00%"
        try:
            return f"{float(v):,.2f}%".replace(".", ",")
        except:
            return str(v)

    def safe(d, *keys, default=None):
        cur = d
        for k in keys:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                return default
        return cur

    # ============ CLASSE PDF CUSTOMIZADA ============
    class RelatorioPDF(FPDF):
        def header(self):
            if self.page_no() > 2:
                self.set_fill_color(*AZUL)
                self.rect(0, 0, 210, 10, "F")
                self.set_font("Helvetica", "B", 9)
                self.set_text_color(255, 255, 255)
                self.set_xy(10, 1)
                self.cell(0, 8, "RELATÓRIO CONSOLIDADO DE ANÁLISE CONTÁBIL", align="L")
                self.set_xy(-60, 1)
                self.cell(50, 8, f"Período: {periodo}", align="R")
                self.set_text_color(0, 0, 0)
                self.ln(15)

        def footer(self):
            if self.page_no() > 2:
                self.set_y(-15)
                self.set_font("Helvetica", "I", 8)
                self.set_text_color(120, 120, 120)
                self.cell(0, 10, f"SGPC - Sistema de Gestão de Prestação de Contas  |  Página {self.page_no()}", align="C")

        def titulo_secao(self, numero, titulo):
            self.add_page()
            self.set_fill_color(*AZUL)
            self.set_text_color(255, 255, 255)
            self.set_font("Helvetica", "B", 16)
            self.cell(0, 14, f"  {numero}. {titulo.upper()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
            self.set_text_color(0, 0, 0)
            self.ln(5)

        def subtitulo(self, texto):
            self.set_font("Helvetica", "B", 11)
            self.set_text_color(*AZUL_CLARO)
            self.cell(0, 8, texto, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_text_color(0, 0, 0)
            self.ln(1)

        def linha_tabela(self, label, valor, destaque=False):
            self.set_font("Helvetica", "B" if destaque else "", 10)
            self.set_fill_color(*(CINZA_CLARO if self.get_y() % 2 == 0 else (255, 255, 255)))
            self.cell(110, 8, "  " + label, border=1, align="L", fill=True)
            self.cell(0, 8, valor + "  ", border=1, align="R", fill=True)
            self.ln()

    # ============ PDF ============
    pdf = RelatorioPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(10, 20, 10)

    # ============ CAPA ============
    pdf.add_page()
    pdf.set_fill_color(*AZUL)
    pdf.rect(0, 0, 210, 80, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_xy(0, 25)
    pdf.cell(210, 15, "RELATÓRIO CONSOLIDADO", align="C")
    pdf.set_font("Helvetica", "", 14)
    pdf.cell(210, 10, "Análise Contábil Executiva", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(60)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Período de Análise", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Helvetica", "", 14)
    pdf.cell(0, 10, periodo, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(20)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Data de Geração: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(40)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*AZUL)
    pdf.cell(0, 6, "SGPC - SISTEMA DE GESTÃO DE PRESTAÇÃO DE CONTAS", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, "Documento Confidencial - Uso Exclusivo da Diretoria", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    # ============ SUMÁRIO ============
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*AZUL)
    pdf.cell(0, 15, "SUMÁRIO", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 12)
    itens = [
        "3. Integridade entre Demonstrações",
        "4. Análise BP",
        "5. Análise BO",
        "6. Análise BF",
        "7. Análise DFC",
        "8. Análise DVP",
        "9. Comparativo de Receitas",
        "10. Comparativo de Despesas",
        "11. Índices de Liquidez",
        "12. Panorama de Resultados",
        "13. Análise Centro de Custos",
        "14. Custo de Pessoal",
    ]
    for item in itens:
        pdf.cell(0, 9, item, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ============ SEÇÕES ============
    # 3 - Integridade
    pdf.titulo_secao(3, "Integridade entre Demonstrações")
    if "integridade" in modulos:
        d = modulos["integridade"].get("dados", {})
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, f"Status: {d.get('status', 'Verificado')}")
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado para o período.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # 4 - Análise BP
    pdf.titulo_secao(4, "Análise BP")
    if "analise_bp" in modulos:
        d = modulos["analise_bp"].get("dados", {})
        inner = safe(d, "dados", default=d)
        pdf.subtitulo("Balanço Patrimonial")
        for chave, valor in inner.items():
            if isinstance(valor, dict) and "atual" in valor:
                pdf.linha_tabela(chave.replace("_", " ").title(), f"Atual: {fmt_moeda(valor.get('atual'))} | Anterior: {fmt_moeda(valor.get('anterior'))}")
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # 5 - Análise BO
    pdf.titulo_secao(5, "Análise BO")
    if "analise_orcamentaria" in modulos:
        d = modulos["analise_orcamentaria"].get("dados", {})
        inner = safe(d, "dados", default=d)
        pdf.subtitulo("Balanço Orçamentário")
        for chave, valor in inner.items():
            if isinstance(valor, (str, int, float)):
                pdf.linha_tabela(chave.replace("_", " ").title(), fmt_moeda(valor))
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # 6 - Análise BF
    pdf.titulo_secao(6, "Análise BF")
    if "analise_financeira_bf" in modulos:
        d = modulos["analise_financeira_bf"].get("dados", {})
        inner = safe(d, "dados", default=d)
        pdf.subtitulo("Balanço Financeiro")
        for chave, valor in inner.items():
            if isinstance(valor, (str, int, float)):
                pdf.linha_tabela(chave.replace("_", " ").title(), fmt_moeda(valor))
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # 7 - Análise DFC
    pdf.titulo_secao(7, "Análise DFC")
    if "analise_dfc" in modulos:
        d = modulos["analise_dfc"].get("dados", {})
        inner = safe(d, "dados", default=d)
        pdf.subtitulo("Demonstração do Fluxo de Caixa")
        for chave, valor in inner.items():
            if isinstance(valor, (str, int, float)):
                pdf.linha_tabela(chave.replace("_", " ").title(), fmt_moeda(valor))
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # 8 - Análise DVP
    pdf.titulo_secao(8, "Análise DVP")
    if "analise_patrimonial" in modulos:
        d = modulos["analise_patrimonial"].get("dados", {})
        inner = safe(d, "dados", default=d)
        pdf.subtitulo("Demonstração das Variações Patrimoniais")
        for chave, valor in inner.items():
            if isinstance(valor, (str, int, float)):
                pdf.linha_tabela(chave.replace("_", " ").title(), fmt_moeda(valor))
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # 9 - Comparativo de Receitas
    pdf.titulo_secao(9, "Comparativo de Receitas")
    if "comparativo_receitas" in modulos:
        d = modulos["comparativo_receitas"].get("dados", {})
        atual = safe(d, "atual", default={})
        pdf.subtitulo("Comparativo Consolidado")
        pdf.linha_tabela("Receita Orçada", fmt_moeda(atual.get("orcado_total", 0)))
        pdf.linha_tabela("Receita Realizada", fmt_moeda(atual.get("realizado_total", 0)))
        pdf.linha_tabela("Percentual de Execução", fmt_pct(atual.get("percentual_total", 0)), destaque=True)
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # 10 - Comparativo de Despesas
    pdf.titulo_secao(10, "Comparativo de Despesas")
    if "comparativo_despesas" in modulos:
        d = modulos["comparativo_despesas"].get("dados", {})
        atual = safe(d, "atual", default={})
        pdf.subtitulo("Comparativo Consolidado")
        pdf.linha_tabela("Despesa Orçada", fmt_moeda(atual.get("orcado_total", 0)))
        pdf.linha_tabela("Despesa Empenhada", fmt_moeda(atual.get("empenhado_total", 0)))
        pdf.linha_tabela("Percentual de Execução", fmt_pct(atual.get("percentual_total", 0)), destaque=True)
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # 11 - Índices de Liquidez
    pdf.titulo_secao(11, "Índices de Liquidez")
    if "liquidez" in modulos:
        d = modulos["liquidez"].get("dados", {})
        liq = safe(d, "liquidez", default=safe(d, "dados", "liquidez", default={}))
        pdf.subtitulo("Indicadores de Liquidez")
        for k in ["liquidez_imediata", "liquidez_corrente", "liquidez_seca", "liquidez_geral"]:
            if k in liq:
                pdf.linha_tabela(k.replace("_", " ").title(), fmt_pct(liq[k]))
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # 12 - Panorama
    pdf.titulo_secao(12, "Panorama de Resultados")
    if "panorama" in modulos:
        d = modulos["panorama"].get("dados", {})
        inner = safe(d, "dados", default=d)
        pdf.subtitulo("Resumo Executivo")
        for k, label in [
            ("ativo_total", "Ativo Total"),
            ("passivo_total", "Passivo Total"),
            ("patrimonio_liquido", "Patrimônio Líquido"),
            ("caixa_bp", "Caixa e Equivalentes"),
            ("receita_realizada", "Receitas Realizadas"),
            ("despesa_empenhada", "Despesas Empenhadas"),
            ("superavit_orcamentario", "Resultado Orçamentário"),
            ("superavit_patrimonial", "Superávit Patrimonial"),
            ("superavit_financeiro", "Superávit Financeiro"),
        ]:
            if k in inner:
                pdf.linha_tabela(label, fmt_moeda(inner[k]))
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # 13 - Centro de Custos
    pdf.titulo_secao(13, "Análise Centro de Custos")
    if "centro_custos" in modulos:
        d = modulos["centro_custos"].get("dados", {})
        inner = safe(d, "dados", default=d)
        pdf.subtitulo("Consolidado por Centro")
        for chave, valor in inner.items():
            if isinstance(valor, (str, int, float)):
                pdf.linha_tabela(chave.replace("_", " ").title(), fmt_moeda(valor))
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # 14 - Custo de Pessoal
    pdf.titulo_secao(14, "Custo de Pessoal")
    if "custo_pessoal" in modulos:
        d = modulos["custo_pessoal"].get("dados", {})
        inner = safe(d, "dados", default=d)
        pdf.subtitulo("Análise de Custo de Pessoal")
        for chave, valor in inner.items():
            if isinstance(valor, (str, int, float)):
                pdf.linha_tabela(chave.replace("_", " ").title(), fmt_moeda(valor))
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Gera o PDF
    pdf_bytes = bytes(pdf.output())
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=relatorio_consolidado_{id}.pdf"}
    )
'''

main_code += "\n" + nova_rota

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(main_code)
print("[OK] Rota do PDF consolidado substituída pela versão de ALTO PADRÃO.")
print("\n=== PROXIMO PASSO ===")
print("1. REINICIE o servidor uvicorn.")
print("2. Aperte Ctrl+Shift+R no navegador.")
print("3. Selecione um histórico e clique em Gerar PDF.")
