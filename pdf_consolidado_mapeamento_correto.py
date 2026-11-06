import re, shutil, datetime

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_pdf_fix_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

# Remove rota antiga
padrao = re.compile(
    r'@app\.get\("/gerar_pdf_relatorio_consolidado/\{id\}"\).*?(?=\n@app\.|\Z)',
    re.DOTALL
)
main_code = padrao.sub("", main_code)

# Nova rota correta
nova_rota = '''
@app.get("/gerar_pdf_relatorio_consolidado/{id}")
def gerar_pdf_relatorio_consolidado(id: int):
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

    # Mapeamento correto (baseado na auditoria)
    # Ordem: chave do módulo, tabela, template da rota (com {id} ou parâmetros extras)
    rotas_pdf = [
        ("integridade", "historico_integridade_matriz", "/gerar_pdf_integridade_matriz/{id}"),
        ("analise_bp", "historico_analise_bp", "/gerar_pdf_analise_bp/{id}"),
        ("analise_orcamentaria", "historico_analise_orcamentaria", "/gerar_pdf_analise_orcamentaria/{id}"),
        ("analise_financeira_bf", "historico_analise_financeira_bf", "/gerar_pdf_analise_financeira_bf/{id}"),
        ("analise_dfc", "historico_analise_dfc", "/gerar_pdf_analise_dfc/{id}"),
        ("analise_patrimonial", "historico_analise_patrimonial", "/gerar_pdf_analise_patrimonial/{id}"),
        ("comparativo_receitas", None, "/gerar_pdf_comparativo_receitas?periodo={periodo}"),
        ("comparativo_despesas", None, "/gerar_pdf_comparativo_despesas?periodo={periodo}"),
        ("liquidez", "historico_liquidez", "/gerar_pdf_liquidez/{id}"),
        ("panorama", "historico_panorama", "/gerar_pdf_panorama/{id}"),
        ("centro_custos", "historico_centro_custos", "/gerar_pdf_centro_custos/{id}"),
        ("custo_pessoal", "historico_custo_pessoal", "/gerar_pdf_custo_pessoal?id={id}"),
    ]

    # Capa (HTML)
    capa_html = f"""<html><head><meta charset="UTF-8"><style>
        @page {{ size: A4; margin: 0; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; }}
        .capa {{ width: 210mm; height: 297mm; background: white; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }}
        .faixa {{ background: #003366; color: white; width: 100%; padding: 50px 0; margin-bottom: 60px; }}
        .faixa img {{ max-height: 100px; margin-bottom: 20px; }}
        .faixa h1 {{ font-size: 34px; margin: 0; letter-spacing: 4px; }}
        .faixa h2 {{ font-size: 16px; margin: 10px 0 0 0; font-weight: 300; }}
        .entidade {{ font-size: 16px; color: #555; margin-bottom: 40px; }}
        .info {{ background: #f4f6f9; border-left: 6px solid #0056b3; padding: 25px 50px; margin: 15px 0; text-align: left; }}
        .info strong {{ display: block; font-size: 12px; color: #666; text-transform: uppercase; margin-bottom: 5px; }}
        .info span {{ font-size: 24px; font-weight: bold; color: #003366; }}
        .rodape {{ position: absolute; bottom: 40px; font-size: 10px; color: #999; }}
    </style></head><body>
    <div class="capa">
        <div class="faixa">
            <img src="http://127.0.0.1:9994/pc_frontend/logo-cofen.png">
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
    </body></html>"""

    pdfs_gerados = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        # Capa
        page.set_content(capa_html, wait_until="networkidle")
        page.wait_for_timeout(500)
        pdfs_gerados.append(page.pdf(format="A4", print_background=True, margin={"top":"0","bottom":"0","left":"0","right":"0"}))

        # Módulos
        for chave, tabela, rota_template in rotas_pdf:
            if chave not in modulos:
                print(f"[SKIP] {chave} não está no consolidado.")
                continue
            
            if "{id}" in rota_template:
                hid = buscar_id_historico(tabela)
                if not hid:
                    print(f"[SKIP] {chave}: sem histórico.")
                    continue
                rota = rota_template.replace("{id}", str(hid))
            elif "{periodo}" in rota_template:
                rota = rota_template.replace("{periodo}", periodo)
            else:
                rota = rota_template

            url = f"http://127.0.0.1:9994{rota}"
            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(1500)
                pdf_mod = page.pdf(format="A4", print_background=True, margin={"top":"10mm","bottom":"10mm","left":"10mm","right":"10mm"})
                pdfs_gerados.append(pdf_mod)
                print(f"[OK] {chave}: {len(pdf_mod)} bytes")
            except Exception as e:
                print(f"[ERRO] {chave}: {e}")

        browser.close()

    writer = PdfWriter()
    for pdf_bytes in pdfs_gerados:
        try:
            reader = PdfReader(BytesIO(pdf_bytes))
            for page in reader.pages:
                writer.add_page(page)
        except Exception as e:
            print(f"[ERRO] Adicionar PDF: {e}")

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
print("[OK] Rota do PDF consolidado reescrita com mapeamento correto.")
print("\n=== PROXIMO PASSO ===")
print("1. REINICIE o servidor uvicorn.")
print("2. Aperte Ctrl+Shift+R no navegador.")
print("3. Selecione um histórico e clique em Gerar PDF.")
