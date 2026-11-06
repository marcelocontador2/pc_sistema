import re, shutil, datetime

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_consolidado_fix_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

# Remove a rota antiga
padrao = re.compile(
    r'@app\.get\("/gerar_pdf_relatorio_consolidado/\{id\}"\).*?(?=\n@app\.|\Z)',
    re.DOTALL
)
main_code = padrao.sub("", main_code)

nova_rota = '''
@app.get("/gerar_pdf_relatorio_consolidado/{id}")
def gerar_pdf_relatorio_consolidado(id: int):
    from playwright.sync_api import sync_playwright
    from pypdf import PdfWriter, PdfReader
    from fastapi.responses import Response
    from io import BytesIO
    import sqlite3, json, os, requests

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, resultado_json FROM historico_relatorio_consolidado WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return Response(content="Histórico não encontrado.", status_code=404, media_type="text/plain")

    periodo, resultado_json = row
    modulos = json.loads(resultado_json).get("dados", {})

    def buscar_id(tabela):
        try:
            conn2 = sqlite3.connect(db_path)
            cur2 = conn2.cursor()
            cur2.execute(f"SELECT id FROM {tabela} WHERE periodo LIKE ? ORDER BY id DESC LIMIT 1", (f"%{periodo}%",))
            r = cur2.fetchone()
            conn2.close()
            return r[0] if r else None
        except:
            return None

    mapeamento = [
        ("integridade",            "historico_integridade_matriz",       "/gerar_pdf_integridade_matriz/{p}",    "id"),
        ("analise_bp",             "historico_analise_bp",               "/gerar_pdf_analise_bp/{p}",            "id"),
        ("analise_orcamentaria",   "historico_analise_orcamentaria",     "/gerar_pdf_analise_orcamentaria/{p}",  "id"),
        ("analise_financeira_bf",  "historico_analise_financeira_bf",    "/gerar_pdf_analise_financeira_bf/{p}", "id"),
        ("analise_dfc",            "historico_analise_dfc",              "/gerar_pdf_analise_dfc/{p}",           "id"),
        ("analise_patrimonial",    "historico_analise_patrimonial",      "/gerar_pdf_analise_patrimonial/{p}",   "id"),
        ("comparativo_receitas",   None,                                 "/gerar_pdf_comparativo_receitas",      "periodo"),
        ("comparativo_despesas",   None,                                 "/gerar_pdf_comparativo_despesas",      "periodo"),
        ("liquidez",               "historico_liquidez",                 "/gerar_pdf_liquidez/{p}",              "id"),
        ("panorama",               "historico_panorama",                 "/gerar_pdf_panorama/{p}",              "id"),
        ("centro_custos",          "historico_centro_custos",            "/gerar_pdf_centro_custos/{p}",         "id"),
        ("custo_pessoal",          "historico_custo_pessoal",            "/gerar_pdf_completo_custo_pessoal",    "query_id"),
    ]

    # Capa
    capa_html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
        @page {{ size: A4; margin: 0; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; }}
        .capa {{ width: 210mm; height: 297mm; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; background: white; }}
        .faixa {{ background: #003366; color: white; width: 100%; padding: 60px 0; margin-bottom: 60px; }}
        .faixa img {{ max-height: 100px; margin-bottom: 25px; }}
        .faixa h1 {{ font-size: 34px; margin: 0; letter-spacing: 5px; font-weight: bold; }}
        .faixa h2 {{ font-size: 16px; margin: 10px 0 0 0; font-weight: normal; }}
        .entidade {{ font-size: 16px; color: #555; margin-bottom: 40px; }}
        .info {{ background: #f4f6f9; border-left: 6px solid #0056b3; padding: 25px 60px; margin: 15px 0; text-align: left; }}
        .info strong {{ display: block; font-size: 11px; color: #666; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 1px; }}
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

    writer = PdfWriter()

    # 1) CAPA (via Playwright)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(capa_html, wait_until="networkidle")
        page.wait_for_timeout(300)
        capa_pdf = page.pdf(format="A4", print_background=True, margin={"top":"0","bottom":"0","left":"0","right":"0"})
        browser.close()
    capa_reader = PdfReader(BytesIO(capa_pdf))
    for page_obj in capa_reader.pages:
        writer.add_page(page_obj)
    print("[OK] Capa gerada")

    # 2) MÓDULOS (via requests + pypdf)
    for chave, tabela, rota_template, tipo in mapeamento:
        if chave not in modulos:
            print(f"[SKIP] {chave} (não está no consolidado)")
            continue

        hid = None
        if tipo in ("id", "query_id") and tabela:
            hid = buscar_id(tabela)
            if not hid:
                print(f"[SKIP] {chave} (sem histórico)")
                continue

        if tipo == "id":
            rota = rota_template.replace("{p}", str(hid))
        elif tipo == "query_id":
            rota = f"{rota_template}?id={hid}"
        else:
            rota = f"{rota_template}?periodo={periodo}"

        url = f"http://127.0.0.1:9994{rota}"
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 200 and r.headers.get("content-type", "").startswith("application/pdf"):
                pdf_reader = PdfReader(BytesIO(r.content))
                for page_obj in pdf_reader.pages:
                    writer.add_page(page_obj)
                print(f"[OK] {chave} ({len(r.content)} bytes)")
            else:
                print(f"[ERRO] {chave}: status={r.status_code}, content-type={r.headers.get('content-type')}")
        except Exception as e:
            print(f"[ERRO] {chave}: {e}")

    output = BytesIO()
    writer.write(output)
    output.seek(0)

    return Response(
        content=output.read(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=relatorio_consolidado_{id}.pdf"}
    )
'''

main_code += "\n" + nova_rota

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(main_code)
print("[OK] Rota corrigida: usa requests+pypdf para os módulos e Playwright só para a capa.")
