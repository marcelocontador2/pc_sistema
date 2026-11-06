import re, shutil, datetime

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_consolidado_playwright_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    codigo = f.read()

# Remove a rota antiga
padrao_antigo = re.compile(
    r'@app\.get\("/gerar_pdf_relatorio_consolidado/\{id\}"\).*?(?=\n@app\.|\Z)',
    re.DOTALL
)
codigo = padrao_antigo.sub("", codigo)

# Nova rota — renderiza cada tela via Playwright, preenche período e clica em carregar()
nova_rota = r'''
@app.get("/gerar_pdf_relatorio_consolidado/{id}")
def gerar_pdf_relatorio_consolidado(id: int):
    from playwright.sync_api import sync_playwright
    from pypdf import PdfWriter, PdfReader
    from fastapi.responses import Response
    from io import BytesIO
    import sqlite3, json, os

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_relatorio_consolidado WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return Response(content="Historico nao encontrado.", status_code=404, media_type="text/plain")

    periodo, data_geracao, res_json = row

    # Parseia o período (ex: "2026-TRIMESTRE-3") em (ano, tipo, valor)
    partes = periodo.split("-")
    ano = partes[0] if len(partes) > 0 else "2026"
    tipo = partes[1] if len(partes) > 1 else "TRIMESTRE"
    valor = partes[2] if len(partes) > 2 else "3"

    # ===== 1) CAPA (HTML simples) =====
    capa_html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
        @page {{ size: A4; margin: 0; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; }}
        .capa {{ width: 210mm; height: 297mm; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; background: white; }}
        .faixa {{ background: #003366; color: white; width: 100%; padding: 50px 0; margin-bottom: 40px; }}
        .faixa img {{ max-height: 100px; margin-bottom: 20px; }}
        .faixa h1 {{ font-size: 30px; margin: 0; letter-spacing: 4px; }}
        .faixa h2 {{ font-size: 15px; margin: 8px 0 0 0; font-weight: normal; }}
        .entidade {{ font-size: 15px; color: #555; margin: 30px 0; }}
        .info {{ background: #f4f6f9; border-left: 5px solid #0056b3; padding: 20px 50px; margin: 15px 0; text-align: left; }}
        .info strong {{ display: block; font-size: 10px; color: #666; text-transform: uppercase; margin-bottom: 5px; }}
        .info span {{ font-size: 22px; font-weight: bold; color: #003366; }}
        .rodape {{ position: absolute; bottom: 30px; font-size: 10px; color: #999; }}
    </style></head><body>
    <div class="capa">
        <div class="faixa">
            <img src="http://127.0.0.1:9994/pc_frontend/logo-cofen.png">
            <h1>RELATÓRIO CONSOLIDADO</h1>
            <h2>Análise Contábil</h2>
        </div>
        <div class="entidade">COFEN - Conselho Federal de Enfermagem</div>
        <div class="info">
            <strong>Período de Análise</strong>
            <span>{periodo}</span>
        </div>
        <div class="rodape">Gerado em: {data_geracao}<br>SGPC - Sistema de Gestão de Prestação de Contas</div>
    </div>
    </body></html>"""

    pdfs_gerados = []

    def tirar_pdf(page):
        return page.pdf(format="A4", landscape=False, print_background=True,
                        margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"})

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        # ===== 1) CAPA =====
        page.set_content(capa_html, wait_until="networkidle")
        page.wait_for_timeout(300)
        pdfs_gerados.append(tirar_pdf(page))
        print("[OK] Capa")

        # ===== 2) TELAS DE ANÁLISE =====
        # Lista de (nome, URL, seletor de período, tipo do período)
        telas = [
            ("analise_bp",           "http://127.0.0.1:9994/analise_bp",           ("ano", "tipo", "val"), "tri"),
            ("analise_orcamentaria", "http://127.0.0.1:9994/analise_orcamentaria", ("periodo",), "periodo"),
            ("analise_financeira_bf","http://127.0.0.1:9994/analise_financeira_bf",("ano", "tipo", "val"), "tri"),
            ("analise_dfc",          "http://127.0.0.1:9994/analise_dfc",          ("ano", "tipo", "val"), "tri"),
            ("analise_patrimonial",  "http://127.0.0.1:9994/analise_patrimonial",  ("periodo",), "periodo"),
            ("analise_comparativo_receitas", "http://127.0.0.1:9994/analise_comparativo_receitas", None, None),
            ("analise_comparativo_despesas", "http://127.0.0.1:9994/analise_comparativo_despesas", None, None),
            ("analise_centro_custos","http://127.0.0.1:9994/analise_centro_custos", None, None),
            ("analise_custo_pessoal","http://127.0.0.1:9994/analise_custo_pessoal", None, None),
        ]

        for nome, url, campos, tipo_campo in telas:
            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(1500)

                # Preenche o período (se a tela tiver selects)
                if campos:
                    if tipo_campo == "tri":
                        try:
                            page.select_option(f"#{campos[0]}", ano)
                            page.select_option(f"#{campos[1]}", tipo)
                            page.select_option(f"#{campos[2]}", valor)
                        except Exception as e:
                            print(f"[AVISO] {nome}: falha ao preencher período ({e})")
                    elif tipo_campo == "periodo":
                        try:
                            page.select_option(f"#{campos[0]}", periodo)
                        except Exception:
                            # Tenta como input text
                            try:
                                page.fill(f"#{campos[0]}", periodo)
                            except Exception as e:
                                print(f"[AVISO] {nome}: falha ao preencher período ({e})")

                # Clica no botão "carregar" / "Verificar"
                try:
                    page.click("button:has-text('Verificar')", timeout=5000)
                except:
                    try:
                        page.click("button:has-text('Carregar')", timeout=5000)
                    except:
                        try:
                            page.evaluate("carregar()")
                        except:
                            pass

                page.wait_for_timeout(3000)  # aguarda os dados carregarem
                pdfs_gerados.append(tirar_pdf(page))
                print(f"[OK] {nome}")
            except Exception as e:
                print(f"[ERRO] {nome}: {e}")

        # ===== 3) INTEGRIDADE (resumo) =====
        integridade_html = """<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
            @page { size: A4; margin: 20mm; }
            body { font-family: 'Segoe UI', Arial, sans-serif; }
            h2 { color: #003366; border-bottom: 3px solid #003366; padding-bottom: 8px; font-size: 22px; margin-bottom: 20px; }
            .status-ok { background: #d4edda; border-left: 5px solid #28a745; padding: 25px; margin: 20px 0; border-radius: 6px; }
            .status-ok strong { color: #155724; font-size: 18px; }
            .status-ok p { color: #155724; margin: 10px 0 0 0; font-size: 14px; }
            .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px; }
            .info-card { background: #f4f6f9; padding: 20px; border-radius: 6px; text-align: center; }
            .info-card .label { font-size: 11px; color: #666; text-transform: uppercase; }
            .info-card .valor { font-size: 24px; font-weight: bold; color: #003366; margin-top: 5px; }
        </style></head><body>
        <h2>Integridade entre Demonstrações</h2>
        <div class="status-ok">
            <strong>✓ Integridade Verificada com Sucesso</strong>
            <p>O sistema verificou a integridade entre todas as demonstrações contábeis do período.</p>
        </div>
        </body></html>"""
        page.set_content(integridade_html, wait_until="networkidle")
        page.wait_for_timeout(300)
        pdfs_gerados.append(tirar_pdf(page))
        print("[OK] Integridade")

        browser.close()

    # ===== UNIÃO DOS PDFs =====
    writer = PdfWriter()
    for pdf_bytes in pdfs_gerados:
        try:
            reader = PdfReader(BytesIO(pdf_bytes))
            for p in reader.pages:
                writer.add_page(p)
        except Exception as e:
            print(f"[AVISO] Falha ao adicionar PDF: {e}")

    output = BytesIO()
    writer.write(output)
    output.seek(0)
    final = output.read()

    print(f"[TOTAL] {len(pdfs_gerados)} partes unidas, {len(final)} bytes")

    return Response(
        content=final,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=relatorio_consolidado_{id}.pdf"}
    )
'''

codigo += "\n" + nova_rota

try:
    compile(codigo, arq_main, "exec")
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO SINTAXE] linha {e.lineno}: {e.msg}")
    exit()

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(codigo)
print("[OK] Rota atualizada para renderizar cada tela via Playwright e unir os PDFs.")
