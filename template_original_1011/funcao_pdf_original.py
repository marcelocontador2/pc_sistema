def gerar_pdf_relatorio_consolidado(id: int):
    import sqlite3, json, os
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    from fastapi.responses import Response
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao FROM historico_relatorio_consolidado WHERE id = ?", (id,))
    row = cursor.fetchone()
    
    # Pega dados da entidade
    cursor.execute("""CREATE TABLE IF NOT EXISTS configuracoes_entidade (
        id INTEGER PRIMARY KEY AUTOINCREMENT, razao_social TEXT, nome_fantasia TEXT, cnpj TEXT, endereco TEXT,
        email TEXT, telefone TEXT, contador_nome TEXT, contador_crc TEXT, contador_uf TEXT, contador_cpf TEXT, contador_email TEXT, data_atualizacao TEXT, logo_path TEXT)""")
    cursor.execute("SELECT * FROM configuracoes_entidade ORDER BY id DESC LIMIT 1")
    ent = cursor.fetchone()
    conn.close()
    
    if not row:
        return Response(content="Historico nao encontrado.", status_code=404)
    
    periodo, data_geracao = row
    
    # Dados da entidade
    razao = ent[1] if ent and len(ent) > 1 else "COFEN/BR"
    cnpj = ent[3] if ent and len(ent) > 3 else ""
    contador_nome = ent[7] if ent and len(ent) > 7 else ""
    contador_crc = ent[8] if ent and len(ent) > 8 else ""
    contador_uf = ent[9] if ent and len(ent) > 9 else ""
    contador_cpf = ent[10] if ent and len(ent) > 10 else ""
    logo_path = ent[13] if ent and len(ent) > 13 else ""
    
    pdf = FPDF()
    pdf.add_page()
    
    # CAPA
    # Logo (se existir)
    caminho_logo = ""
    if logo_path:
        if os.path.isabs(logo_path):
            caminho_logo = logo_path
        else:
            caminho_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_logos", logo_path)
        if not os.path.exists(caminho_logo):
            caminho_logo = ""
    
    if caminho_logo:
        try:
            # Centraliza a logo no topo
            pdf.image(caminho_logo, x=70, y=20, w=70)
            y_inicio = 100
        except Exception:
            y_inicio = 50
    else:
        y_inicio = 50
    
    # Titulo
    pdf.set_y(y_inicio)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "RELATORIO CONSOLIDADO", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "DE ANALISE CONTABIL", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"Periodo: {periodo}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 8, f"Data de Emissao: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    pdf.ln(30)
    
    # Dados da entidade na capa
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 8, "DADOS DA ENTIDADE", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, f"Razao Social: {razao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 6, f"CNPJ: {cnpj}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    pdf.ln(20)
    
    # Dados do contador na capa
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 8, "RESPONSAVEL TECNICO", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, f"Contador: {contador_nome}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 6, f"CRC: {contador_crc} / UF: {contador_uf}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 6, f"CPF: {contador_cpf}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    # ========== PAGINA 2: SUMARIO ==========
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "SUMARIO", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)
    
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    capitulos = [
        "1. Apresentacao e Escopo",
        "2. Visao Geral Orcamentaria e Financeira",
        "3. Analise do Balanco Patrimonial",
        "4. Demonstracao das Variacoes Patrimoniais",
        "5. Demonstracao dos Fluxos de Caixa",
        "6. Demonstracao das Mutacoes do PL",
        "7. Analise de Despesas e Custeio",
        "8. Matriz de Integridade e Controles",
        "9. Parecer Conclusivo",
        "10. Anexos e Assinaturas"
    ]
    for cap in capitulos:
        pdf.cell(0, 8, cap, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # ========== PAGINA FINAL: ASSINATURA ==========
    pdf.add_page()
    pdf.set_y(100)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "_____________________________________________", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 8, "Contador Responsavel", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, contador_nome, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"CRC: {contador_crc} / UF: {contador_uf}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 8, f"CPF: {contador_cpf}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    pdf_bytes = bytes(pdf.output())
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=Relatorio_Consolidado_{periodo}.pdf"})
