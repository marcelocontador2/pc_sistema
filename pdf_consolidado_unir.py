import re, shutil, datetime

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_pdf_uniao_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

# Remove a rota antiga do PDF (que recriava layout)
padrao_antigo = re.compile(
    r'@app\.get\("/gerar_pdf_relatorio_consolidado/\{id\}"\).*?(?=\n@app\.|\Z)',
    re.DOTALL
)
main_code = padrao_antigo.sub("", main_code)

# Nova rota que UNE os PDFs de cada módulo
nova_rota = '''
@app.get("/gerar_pdf_relatorio_consolidado/{id}")
async def gerar_pdf_relatorio_consolidado(id: int):
    from playwright.sync_api import sync_playwright
    from pypdf import PdfWriter, PdfReader
    from fastapi.responses import Response
    from io import BytesIO
    import sqlite3, json, os, time

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, resultado_json FROM historico_relatorio_consolidado WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return Response(content="Histórico não encontrado.", status_code=404, media_type="text/plain")

    periodo, resultado_json = row
    dados = json.loads(resultado_json)
    modulos = dados.get("dados", {})

    # ============ MAPEAMENTO: módulo -> rota do PDF dele ============
    # Para cada módulo, precisamos saber o ID do histórico DELE para gerar o PDF individual.
    # Vamos buscar o último registro de cada tabela específica para o período.
    def buscar_id_historico(tabela):
        try:
            conn2 = sqlite3.connect(db_path)
            cur2 = conn2.cursor()
            cur2.execute(f"SELECT id FROM {tabela} WHERE periodo LIKE ? ORDER BY id DESC LIMIT 1", (f"%{periodo}%",))
            r = cur2.fetchone()
            conn2.close()
            return r[0] if r else None
        except:
            return None

    rotas_pdf = {
        "analise_bp": ("historico_analise_bp", "/gerar_pdf_analise_bp/{hid}"),
        "analise_orcamentaria": ("historico_analise_orcamentaria", "/gerar_pdf_analise_orcamentaria/{hid}"),
        "analise_financeira_bf": ("historico_analise_financeira_bf", "/gerar_pdf_analise_financeira_bf/{hid}"),
        "analise_dfc": ("historico_analise_dfc", "/gerar_pdf_analise_dfc/{hid}"),
        "analise_patrimonial": ("historico_analise_patrimonial", "/gerar_pdf_analise_patrimonial/{hid}"),
        "comparativo_receitas": ("historico_comparativo_receitas", "/gerar_pdf_comparativo_receitas"),
        "comparativo_despesas": ("historico_comparativo_despesas", "/gerar_pdf_comparativo_despesas"),
        "liquidez": ("historico_liquidez", "/gerar_pdf_liquidez/{hid}"),
        "panorama": ("historico_panorama", "/gerar_pdf_panorama/{hid}"),
        "centro_custos": ("historico_centro_custos", "/gerar_pdf_centro_custos/{hid}"),
        "custo_pessoal": ("historico_custo_pessoal", "/gerar_pdf_custo_pessoal?id={hid}"),
        "integridade": ("historico_integridade_matriz", "/gerar_pdf_integridade_matriz/{hid}"),
    }

    # ============ GERA A CAPA (HTML simples) ============
    capa_html = f"""
    <html><head><meta charset="UTF-8"><style>
        @page {{ size: A4; margin: 0; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; }}
        .capa {{ width: 210mm; height: 297mm; background: white; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }}
        .faixa {{ background: #003366; color: white; width: 100%; padding: 40px 0; margin-bottom: 60px; }}
        .faixa img {{ max-height: 100px; margin-bottom: 20px; }}
        .faixa h1 {{ font-size: 36px; margin: 0; letter-spacing: 4px; }}
        .faixa h2 {{ font-size: 18px; margin: 10px 0 0 0; font-weight: 300; }}
        .entidade {{ font-size: 16px; color: #555; margin-bottom: 40px; }}
        .info {{ background: #f4f6f9; border-left: 6px solid #0056b3; padding: 25px 50px; margin: 15px 0; text-align: left; }}
        .info strong {{ display: block; font-size: 12px; color: #666; text-transform: uppercase; margin-bottom: 5px; }}
        .info span {{ font-size: 24px; font-weight: bold; color: #003366; }}
        .rodape {{ position: absolute; bottom: 40px; font-size: 10px; color: #999; }}
    </style></head><body>
    <div class="capa">
        <div class="faixa">
            <img src="http://127.0.0.1:9994/pc_frontend/logo-cofen.png" alt="COFEN">
            <h1>RELATÓRIO CONSOLIDADO</h1>
            <h2>Análise Contábil Executiva</h2>
        </div>
        <div class="entidade">COFEN - Conselho Federal de Enfermagem</div>
        <div class="info">
            <strong>Período de Análise</strong>
            <span>{periodo}</span>
        </div>
        <div class="rodape">SGPC - Sistema de Gestão de Prestação de Contas<br><i>Documento Confidencial - Uso Exclusivo da Diretoria</i></div>
    </div>
    </body></html>
    """

    # ============ GERA CADA PDF INDIVIDUAL ============
    pdfs_gerados = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        # Capa
        page.set_content(capa_html, wait_until="networkidle")
        page.wait_for_timeout(500)
        capa_bytes = page.pdf(format="A4", print_background=True, margin={"top":"0","bottom":"0","left":"0","right":"0"})
        pdfs_gerados.append(capa_bytes)

        # Cada módulo
        for chave, (tabela, rota_template) in rotas_pdf.items():
            if chave not in modulos:
                continue
            hid = buscar_id_historico(tabela)
            if not hid:
                continue
            rota = rota_template.replace("{hid}", str(hid))
            url = f"http://127.0.0.1:9994{rota}"
            
            try:
                page.goto(url, wait_until="networkidle", timeout=15000)
                page.wait_for_timeout(1500)
                pdf_mod = page.pdf(format="A4", print_background=True, margin={"top":"10mm","bottom":"10mm","left":"10mm","right":"10mm"})
                pdfs_gerados.append(pdf_mod)
            except Exception as e:
                print(f"[AVISO] Falha ao gerar PDF de {chave}: {e}")

        browser.close()

    # ============ UNE OS PDFs ============
    writer = PdfWriter()
    for pdf_bytes in pdfs_gerados:
        try:
            reader = PdfReader(BytesIO(pdf_bytes))
            for page in reader.pages:
                writer.add_page(page)
        except Exception as e:
            print(f"[AVISO] Falha ao adicionar PDF: {e}")

    output = BytesIO()
    writer.write(output)
    output.seek(0)
    final_bytes = output.read()

    return Response(
        content=final_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=relatorio_consolidado_{id}.pdf"}
    )
'''

main_code += "\n" + nova_rota

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(main_code)
print("[OK] Rota do PDF consolidado alterada para UNIR os PDFs de cada módulo.")
print("\n=== PROXIMO PASSO ===")
print("1. REINICIE o servidor uvicorn.")
print("2. Aperte Ctrl+Shift+R no navegador.")
print("3. Selecione um histórico e clique em Gerar PDF.")
