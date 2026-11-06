import re, shutil, datetime

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_pdf_premium2_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

# Remove a rota antiga do PDF consolidado
padrao_antigo = re.compile(
    r'@app\.get\("/gerar_pdf_relatorio_consolidado/\{id\}"\).*?(?=\n@app\.|\Z)',
    re.DOTALL
)
main_code = padrao_antigo.sub("", main_code)

# Nova rota premium com logo, dados reais e layout executivo
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

    # ============ CORES E UTILITÁRIOS ============
    AZUL = (0, 51, 102)
    AZUL_CLARO = (0, 86, 179)
    CINZA_CLARO = (245, 247, 250)
    CINZA_HEADER = (220, 225, 230)
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

    def limpar(s):
        return str(s).replace("_", " ").title()

    # ============ CLASSE PDF ============
    class RelatorioPDF(FPDF):
        def header(self):
            if self.page_no() > 2:
                self.set_fill_color(*AZUL)
                self.rect(0, 0, 210, 12, "F")
                self.set_font("Helvetica", "B", 9)
                self.set_text_color(255, 255, 255)
                self.set_xy(10, 2)
                self.cell(100, 8, "RELATÓRIO CONSOLIDADO DE ANÁLISE CONTÁBIL", align="L")
                self.set_xy(120, 2)
                self.cell(80, 8, f"Período: {periodo}", align="R")
                self.set_text_color(0, 0, 0)
                self.ln(15)

        def footer(self):
            if self.page_no() > 2:
                self.set_y(-15)
                self.set_font("Helvetica", "I", 8)
                self.set_text_color(120, 120, 120)
                self.cell(0, 10, f"COFEN - Conselho Federal de Enfermagem  |  Página {self.page_no()}", align="C")

        def titulo_secao(self, numero, titulo):
            self.add_page()
            self.set_fill_color(*AZUL)
            self.set_text_color(255, 255, 255)
            self.set_font("Helvetica", "B", 15)
            self.cell(0, 12, f"  {numero}. {titulo.upper()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
            self.set_text_color(0, 0, 0)
            self.ln(4)

        def subtitulo(self, texto):
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(*AZUL_CLARO)
            self.cell(0, 7, texto, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_text_color(0, 0, 0)
            self.ln(1)

        def header_tabela(self, colunas):
            self.set_fill_color(*CINZA_HEADER)
            self.set_font("Helvetica", "B", 9)
            for col, largura in colunas:
                self.cell(largura, 8, "  " + col, border=1, align="L", fill=True)
            self.ln()

        def linha_tabela(self, valores, larguras, destaque=False):
            self.set_font("Helvetica", "B" if destaque else "", 9)
            self.set_fill_color(*(CINZA_CLARO if self.get_y() % 2 == 0 else (255, 255, 255)))
            for i, (valor, largura) in enumerate(zip(valores, larguras)):
                align = "R" if i > 0 else "L"
                prefixo = "  " if i == 0 else ""
                sufixo = "  " if i > 0 else ""
                self.cell(largura, 7, prefixo + valor + sufixo, border=1, align=align, fill=True)
            self.ln()

    # ============ PDF ============
    pdf = RelatorioPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(10, 20, 10)

    # ============ CAPA ============
    pdf.add_page()
    # Faixa azul superior
    pdf.set_fill_color(*AZUL)
    pdf.rect(0, 0, 210, 70, "F")

    # Logo COFEN (se existir)
    caminho_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "logo-cofen.png")
    if os.path.exists(caminho_logo):
        pdf.image(caminho_logo, x=85, y=15, w=40)

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_xy(0, 60)
    pdf.cell(210, 12, "RELATÓRIO CONSOLIDADO", align="C")

    pdf.set_text_color(0, 0, 0)
    pdf.set_y(85)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "COFEN - Conselho Federal de Enfermagem", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, "Análise Contábil Executiva", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)

    # Período em destaque
    pdf.set_fill_color(*CINZA_CLARO)
    pdf.rect(50, 130, 110, 30, "F")
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*AZUL)
    pdf.set_xy(50, 135)
    pdf.cell(110, 8, "Período de Análise", align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_xy(50, 145)
    pdf.cell(110, 8, periodo, align="C")

    pdf.ln(50)
    pdf.set_y(180)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Data de Geração: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(30)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*AZUL)
    pdf.cell(0, 6, "SGPC - SISTEMA DE GESTÃO DE PRESTAÇÃO DE CONTAS", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, "Documento Confidencial - Uso Exclusivo da Diretoria", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    # ============ SUMÁRIO ============
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*AZUL)
    pdf.cell(0, 15, "SUMÁRIO", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 11)
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

    # ============ 3. INTEGRIDADE ============
    pdf.titulo_secao(3, "Integridade entre Demonstrações")
    if "integridade" in modulos:
        d = modulos["integridade"].get("dados", {})
        inner = safe(d, "dados", default=d)
        if isinstance(inner, dict):
            total = safe(inner, "total_verificacoes", default="N/A")
            ok = safe(inner, "total_ok", default="N/A")
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 8, f"Total de Verificações: {total}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(0, 8, f"Verificações OK: {ok}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ============ 4. ANÁLISE BP ============
    pdf.titulo_secao(4, "Análise BP")
    if "analise_bp" in modulos:
        d = modulos["analise_bp"].get("dados", {})
        inner = safe(d, "dados", default=d)
        pdf.subtitulo("Balanço Patrimonial")
        pdf.header_tabela([("Conta", 80), ("Atual", 55), ("Anterior", 55)])
        for chave, valor in inner.items():
            if isinstance(valor, dict) and "atual" in valor:
                pdf.linha_tabela([limpar(chave), fmt_moeda(valor.get("atual")), fmt_moeda(valor.get("anterior"))], [80, 55, 55])
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ============ 5. ANÁLISE BO ============
    pdf.titulo_secao(5, "Análise BO")
    if "analise_orcamentaria" in modulos:
        d = modulos["analise_orcamentaria"].get("dados", {})
        inner = safe(d, "dados", default=d)
        pdf.subtitulo("Balanço Orçamentário")
        if isinstance(inner, dict):
            pdf.header_tabela([("Item", 130), ("Valor", 60)])
            for chave, valor in inner.items():
                if isinstance(valor, (str, int, float)):
                    pdf.linha_tabela([limpar(chave), fmt_moeda(valor)], [130, 60])
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ============ 6. ANÁLISE BF ============
    pdf.titulo_secao(6, "Análise BF")
    if "analise_financeira_bf" in modulos:
        d = modulos["analise_financeira_bf"].get("dados", {})
        inner = safe(d, "dados", default=d)
        pdf.subtitulo("Balanço Financeiro")
        if isinstance(inner, dict):
            pdf.header_tabela([("Item", 130), ("Valor", 60)])
            for chave, valor in inner.items():
                if isinstance(valor, (str, int, float)):
                    pdf.linha_tabela([limpar(chave), fmt_moeda(valor)], [130, 60])
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ============ 7. ANÁLISE DFC ============
    pdf.titulo_secao(7, "Análise DFC")
    if "analise_dfc" in modulos:
        d = modulos["analise_dfc"].get("dados", {})
        inner = safe(d, "dados", default=d)
        pdf.subtitulo("Demonstração do Fluxo de Caixa")
        if isinstance(inner, dict):
            pdf.header_tabela([("Item", 130), ("Valor", 60)])
            for chave, valor in inner.items():
                if isinstance(valor, (str, int, float)):
                    pdf.linha_tabela([limpar(chave), fmt_moeda(valor)], [130, 60])
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ============ 8. ANÁLISE DVP ============
    pdf.titulo_secao(8, "Análise DVP")
    if "analise_patrimonial" in modulos:
        d = modulos["analise_patrimonial"].get("dados", {})
        inner = safe(d, "dados", default=d)
        pdf.subtitulo("Demonstração das Variações Patrimoniais")
        if isinstance(inner, dict):
            pdf.header_tabela([("Item", 130), ("Valor", 60)])
            for chave, valor in inner.items():
                if isinstance(valor, (str, int, float)):
                    pdf.linha_tabela([limpar(chave), fmt_moeda(valor)], [130, 60])
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ============ 9. COMPARATIVO DE RECEITAS ============
    pdf.titulo_secao(9, "Comparativo de Receitas")
    if "comparativo_receitas" in modulos:
        d = modulos["comparativo_receitas"].get("dados", {})
        atual = safe(d, "atual", default={})
        pdf.subtitulo("Comparativo Consolidado")
        pdf.header_tabela([("Item", 130), ("Valor", 60)])
        pdf.linha_tabela(["Receita Orçada", fmt_moeda(atual.get("orcado_total", 0))], [130, 60])
        pdf.linha_tabela(["Receita Realizada", fmt_moeda(atual.get("realizado_total", 0))], [130, 60])
        pdf.linha_tabela(["Percentual de Execução", fmt_pct(atual.get("percentual_total", 0))], [130, 60], destaque=True)

        # Grupos
        grupos = atual.get("grupos", [])
        if grupos:
            pdf.ln(3)
            pdf.subtitulo("Composição das Receitas")
            pdf.header_tabela([("Grupo", 80), ("Orçado", 55), ("Realizado", 55)])
            for g in grupos:
                pdf.linha_tabela([g.get("nome", ""), fmt_moeda(g.get("orcado", 0)), fmt_moeda(g.get("realizado", 0))], [80, 55, 55])
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ============ 10. COMPARATIVO DE DESPESAS ============
    pdf.titulo_secao(10, "Comparativo de Despesas")
    if "comparativo_despesas" in modulos:
        d = modulos["comparativo_despesas"].get("dados", {})
        atual = safe(d, "atual", default={})
        pdf.subtitulo("Comparativo Consolidado")
        pdf.header_tabela([("Item", 130), ("Valor", 60)])
        pdf.linha_tabela(["Despesa Orçada", fmt_moeda(atual.get("orcado_total", 0))], [130, 60])
        pdf.linha_tabela(["Despesa Empenhada", fmt_moeda(atual.get("empenhado_total", 0))], [130, 60])
        pdf.linha_tabela(["Percentual de Execução", fmt_pct(atual.get("percentual_total", 0))], [130, 60], destaque=True)

        grupos = atual.get("grupos", [])
        if grupos:
            pdf.ln(3)
            pdf.subtitulo("Composição das Despesas")
            pdf.header_tabela([("Grupo", 80), ("Orçado", 55), ("Empenhado", 55)])
            for g in grupos:
                pdf.linha_tabela([g.get("nome", ""), fmt_moeda(g.get("orcado", 0)), fmt_moeda(g.get("empenhado", 0))], [80, 55, 55])
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ============ 11. ÍNDICES DE LIQUIDEZ ============
    pdf.titulo_secao(11, "Índices de Liquidez")
    if "liquidez" in modulos:
        d = modulos["liquidez"].get("dados", {})
        liq = safe(d, "liquidez", default=safe(d, "dados", "liquidez", default={}))
        pdf.subtitulo("Indicadores de Liquidez")
        pdf.header_tabela([("Indicador", 130), ("Valor", 60)])
        for k, label in [
            ("liquidez_imediata", "Liquidez Imediata"),
            ("liquidez_corrente", "Liquidez Corrente"),
            ("liquidez_seca", "Liquidez Seca"),
            ("liquidez_geral", "Liquidez Geral"),
        ]:
            if k in liq:
                pdf.linha_tabela([label, str(liq[k])], [130, 60])
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ============ 12. PANORAMA ============
    pdf.titulo_secao(12, "Panorama de Resultados")
    if "panorama" in modulos:
        d = modulos["panorama"].get("dados", {})
        inner = safe(d, "dados", default=d)
        pdf.subtitulo("Resumo Executivo")
        pdf.header_tabela([("Indicador", 130), ("Valor", 60)])
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
                pdf.linha_tabela([label, fmt_moeda(inner[k])], [130, 60])
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ============ 13. CENTRO DE CUSTOS ============
    pdf.titulo_secao(13, "Análise Centro de Custos")
    if "centro_custos" in modulos:
        d = modulos["centro_custos"].get("dados", {})
        inner = safe(d, "dados", default=d)
        pdf.subtitulo("Consolidado por Centro de Custos")
        if isinstance(inner, dict):
            pdf.header_tabela([("Centro de Custo", 130), ("Valor", 60)])
            for chave, valor in inner.items():
                if isinstance(valor, (str, int, float)):
                    pdf.linha_tabela([limpar(chave), fmt_moeda(valor)], [130, 60])
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Módulo não encontrado.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ============ 14. CUSTO DE PESSOAL ============
    pdf.titulo_secao(14, "Custo de Pessoal")
    if "custo_pessoal" in modulos:
        d = modulos["custo_pessoal"].get("dados", {})
        inner = safe(d, "dados", default=d)
        pdf.subtitulo("Análise de Custo de Pessoal")
        pdf.header_tabela([("Item", 130), ("Valor", 60)])
        for k, label in [
            ("rcl_atual", "RCL Atual"),
            ("rcl_anterior", "RCL Anterior"),
            ("rcl_total", "RCL Total"),
            ("pessoal_atual", "Pessoal Atual"),
            ("pessoal_anterior", "Pessoal Anterior"),
            ("pessoal_total", "Pessoal Total"),
            ("custo_atual", "Custo Atual"),
            ("custo_anterior", "Custo Anterior"),
            ("custo_total", "Custo Total"),
            ("limite_total", "Limite Total"),
            ("margem_disponivel_total", "Margem Disponível"),
        ]:
            if k in inner:
                pdf.linha_tabela([label, fmt_moeda(inner[k])], [130, 60])
        # Percentual
        if "pct_custo_total" in inner:
            pdf.linha_tabela(["Percentual de Custo", f"{inner['pct_custo_total']}%"], [130, 60], destaque=True)
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
print("[OK] Rota do PDF substituída pela versão premium com logo COFEN e dados reais.")
print("\n=== PROXIMO PASSO ===")
print("1. REINICIE o servidor uvicorn.")
print("2. Aperte Ctrl+Shift+R no navegador.")
print("3. Selecione um histórico e clique em Gerar PDF.")
