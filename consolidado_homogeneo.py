import re, shutil, datetime

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_consolidado_homogeneo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    codigo = f.read()

# Remove a rota antiga do PDF consolidado
padrao_antigo = re.compile(
    r'@app\.get\("/gerar_pdf_relatorio_consolidado/\{id\}"\).*?(?=\n@app\.|\Z)',
    re.DOTALL
)
codigo = padrao_antigo.sub("", codigo)

# =========================================================
# Nova rota: gera TODO o consolidado via Playwright em HTML
# =========================================================
nova_rota = '''
@app.get("/gerar_pdf_relatorio_consolidado/{id}")
def gerar_pdf_relatorio_consolidado(id: int):
    from playwright.sync_api import sync_playwright
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

    periodo, data_geracao, res_json = row
    modulos = json.loads(res_json).get("dados", {})

    # ===== UTILITÁRIOS =====
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

    def safe(d, *keys, default="—"):
        cur = d
        for k in keys:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                return default
        return cur

    # ===== GERA O HTML DO CONSOLIDADO =====
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
        @page {{ size: A4; margin: 15mm; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #333; line-height: 1.4; }}
        h1 {{ color: #003366; }}
        h2 {{ color: #003366; border-bottom: 2px solid #003366; padding-bottom: 5px; page-break-before: always; }}
        h3 {{ color: #0056b3; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th {{ background: #003366; color: white; padding: 8px; text-align: left; border: 1px solid #ccc; font-size: 11px; }}
        td {{ padding: 6px 8px; border: 1px solid #ccc; font-size: 11px; }}
        td.right {{ text-align: right; }}
        tr:nth-child(even) {{ background: #f8f9fa; }}
        .status-ok {{ background: #d4edda; border-left: 5px solid #28a745; padding: 15px; margin: 15px 0; }}
        .status-warn {{ background: #fff3cd; border-left: 5px solid #ffc107; padding: 15px; margin: 15px 0; }}
        .status-erro {{ background: #f8d7da; border-left: 5px solid #dc3545; padding: 15px; margin: 15px 0; }}
        .card-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 15px 0; }}
        .card {{ background: #f4f6f9; padding: 15px; border-radius: 6px; border-left: 4px solid #0056b3; }}
        .card .label {{ font-size: 10px; color: #666; text-transform: uppercase; }}
        .card .valor {{ font-size: 18px; font-weight: bold; color: #003366; margin-top: 5px; }}
        .secao {{ page-break-inside: avoid; }}
        .capa {{ text-align: center; padding-top: 80mm; page-break-after: always; }}
        .capa .faixa {{ background: #003366; color: white; padding: 40px 0; margin: -15mm -15mm 40px -15mm; }}
        .capa h1 {{ color: white; margin: 0; font-size: 32px; letter-spacing: 4px; }}
        .capa h2 {{ color: white; margin: 10px 0 0 0; font-size: 16px; font-weight: normal; border: none; }}
        .capa .entidade {{ font-size: 16px; color: #555; margin: 30px 0; }}
        .capa .info {{ background: #f4f6f9; border-left: 5px solid #0056b3; padding: 20px; margin: 20px auto; max-width: 400px; }}
    </style></head><body>

    <!-- ===== CAPA ===== -->
    <div class="capa">
        <div class="faixa">
            <h1>RELATÓRIO CONSOLIDADO</h1>
            <h2>Análise Contábil</h2>
        </div>
        <div class="entidade">COFEN - Conselho Federal de Enfermagem</div>
        <div class="info">
            <div style="font-size: 12px; color: #666;">PERÍODO DE ANÁLISE</div>
            <div style="font-size: 20px; font-weight: bold; color: #003366;">{periodo}</div>
        </div>
        <p style="color: #999; font-size: 11px; margin-top: 60px;">Gerado em: {data_geracao}</p>
    </div>
    """

    # ===== 1. INTEGRIDADE =====
    html += '<div class="secao"><h2>1. Integridade entre Demonstrações</h2>'
    if "integridade" in modulos:
        d = modulos["integridade"].get("dados", {})
        inner = safe(d, "dados", default=d)
        total = safe(inner, "total_verificacoes", default="N/A")
        ok = safe(inner, "total_ok", default="N/A")
        html += f'''
        <div class="status-ok">
            <strong>✓ Integridade Verificada</strong>
            <p>Total de Verificações: <strong>{total}</strong> | Verificações OK: <strong>{ok}</strong></p>
        </div>'''
    else:
        html += '<div class="status-warn">Módulo não encontrado no histórico.</div>'
    html += '</div>'

    # ===== 2. ANÁLISE BP =====
    html += '<div class="secao"><h2>2. Análise BP</h2>'
    if "analise_bp" in modulos:
        d = modulos["analise_bp"].get("dados", {})
        inner = safe(d, "dados", default=d)
        html += '<table><tr><th>Conta</th><th>Período Atual</th><th>Período Anterior</th></tr>'
        for chave, valor in inner.items():
            if isinstance(valor, dict) and "atual" in valor:
                html += f'<tr><td>{chave.replace("_"," ").title()}</td><td class="right">{fmt_moeda(valor.get("atual"))}</td><td class="right">{fmt_moeda(valor.get("anterior"))}</td></tr>'
        html += '</table>'
    else:
        html += '<div class="status-warn">Módulo não encontrado.</div>'
    html += '</div>'

    # ===== 3. ANÁLISE BO =====
    html += '<div class="secao"><h2>3. Análise BO</h2>'
    if "analise_orcamentaria" in modulos:
        d = modulos["analise_orcamentaria"].get("dados", {})
        inner = safe(d, "dados", default=d)
        html += '<table><tr><th>Item</th><th>Valor</th></tr>'
        for chave, valor in inner.items():
            if isinstance(valor, (str, int, float)):
                html += f'<tr><td>{chave.replace("_"," ").title()}</td><td class="right">{fmt_moeda(valor)}</td></tr>'
        html += '</table>'
    else:
        html += '<div class="status-warn">Módulo não encontrado.</div>'
    html += '</div>'

    # ===== 4. ANÁLISE BF =====
    html += '<div class="secao"><h2>4. Análise BF</h2>'
    if "analise_financeira_bf" in modulos:
        d = modulos["analise_financeira_bf"].get("dados", {})
        inner = safe(d, "dados", default=d)
        html += '<table><tr><th>Item</th><th>Valor</th></tr>'
        for chave, valor in inner.items():
            if isinstance(valor, (str, int, float)):
                html += f'<tr><td>{chave.replace("_"," ").title()}</td><td class="right">{fmt_moeda(valor)}</td></tr>'
        html += '</table>'
    else:
        html += '<div class="status-warn">Módulo não encontrado.</div>'
    html += '</div>'

    # ===== 5. ANÁLISE DFC =====
    html += '<div class="secao"><h2>5. Análise DFC</h2>'
    if "analise_dfc" in modulos:
        d = modulos["analise_dfc"].get("dados", {})
        inner = safe(d, "dados", default=d)
        html += '<table><tr><th>Item</th><th>Valor</th></tr>'
        for chave, valor in inner.items():
            if isinstance(valor, (str, int, float)):
                html += f'<tr><td>{chave.replace("_"," ").title()}</td><td class="right">{fmt_moeda(valor)}</td></tr>'
        html += '</table>'
    else:
        html += '<div class="status-warn">Módulo não encontrado.</div>'
    html += '</div>'

    # ===== 6. ANÁLISE DVP =====
    html += '<div class="secao"><h2>6. Análise DVP</h2>'
    if "analise_patrimonial" in modulos:
        d = modulos["analise_patrimonial"].get("dados", {})
        inner = safe(d, "dados", default=d)
        html += '<table><tr><th>Item</th><th>Valor</th></tr>'
        for chave, valor in inner.items():
            if isinstance(valor, (str, int, float)):
                html += f'<tr><td>{chave.replace("_"," ").title()}</td><td class="right">{fmt_moeda(valor)}</td></tr>'
        html += '</table>'
    else:
        html += '<div class="status-warn">Módulo não encontrado.</div>'
    html += '</div>'

    # ===== 7. COMPARATIVO DE RECEITAS =====
    html += '<div class="secao"><h2>7. Comparativo de Receitas</h2>'
    if "comparativo_receitas" in modulos:
        d = modulos["comparativo_receitas"].get("dados", {})
        atual = safe(d, "atual", default={})
        html += f'''
        <div class="card-grid">
            <div class="card"><div class="label">Receita Orçada</div><div class="valor">{fmt_moeda(atual.get("orcado_total", 0))}</div></div>
            <div class="card"><div class="label">Receita Realizada</div><div class="valor">{fmt_moeda(atual.get("realizado_total", 0))}</div></div>
            <div class="card"><div class="label">% Execução</div><div class="valor">{fmt_pct(atual.get("percentual_total", 0))}</div></div>
        </div>'''
    else:
        html += '<div class="status-warn">Módulo não encontrado.</div>'
    html += '</div>'

    # ===== 8. COMPARATIVO DE DESPESAS =====
    html += '<div class="secao"><h2>8. Comparativo de Despesas</h2>'
    if "comparativo_despesas" in modulos:
        d = modulos["comparativo_despesas"].get("dados", {})
        atual = safe(d, "atual", default={})
        html += f'''
        <div class="card-grid">
            <div class="card"><div class="label">Despesa Orçada</div><div class="valor">{fmt_moeda(atual.get("orcado_total", 0))}</div></div>
            <div class="card"><div class="label">Despesa Empenhada</div><div class="valor">{fmt_moeda(atual.get("empenhado_total", 0))}</div></div>
            <div class="card"><div class="label">% Execução</div><div class="valor">{fmt_pct(atual.get("percentual_total", 0))}</div></div>
        </div>'''
    else:
        html += '<div class="status-warn">Módulo não encontrado.</div>'
    html += '</div>'

    # ===== 9. ÍNDICES DE LIQUIDEZ =====
    html += '<div class="secao"><h2>9. Índices de Liquidez</h2>'
    if "liquidez" in modulos:
        d = modulos["liquidez"].get("dados", {})
        liq = safe(d, "liquidez", default=safe(d, "dados", "liquidez", default={}))
        html += '<table><tr><th>Indicador</th><th>Valor</th></tr>'
        for k, label in [("liquidez_imediata", "Liquidez Imediata"), ("liquidez_corrente", "Liquidez Corrente"), ("liquidez_seca", "Liquidez Seca"), ("liquidez_geral", "Liquidez Geral")]:
            if k in liq:
                html += f'<tr><td>{label}</td><td class="right">{liq[k]}</td></tr>'
        html += '</table>'
    else:
        html += '<div class="status-warn">Módulo não encontrado.</div>'
    html += '</div>'

    # ===== 10. PANORAMA =====
    html += '<div class="secao"><h2>10. Panorama de Resultados</h2>'
    if "panorama" in modulos:
        d = modulos["panorama"].get("dados", {})
        inner = safe(d, "dados", default=d)
        html += '<div class="card-grid">'
        for k, label in [("ativo_total", "Ativo Total"), ("passivo_total", "Passivo Total"), ("patrimonio_liquido", "Patrimônio Líquido"), ("caixa_bp", "Caixa e Equivalentes"), ("receita_realizada", "Receitas Realizadas"), ("despesa_empenhada", "Despesas Empenhadas"), ("superavit_orcamentario", "Resultado Orçamentário"), ("superavit_patrimonial", "Superávit Patrimonial"), ("superavit_financeiro", "Superávit Financeiro")]:
            if k in inner:
                html += f'<div class="card"><div class="label">{label}</div><div class="valor">{fmt_moeda(inner[k])}</div></div>'
        html += '</div>'
    else:
        html += '<div class="status-warn">Módulo não encontrado.</div>'
    html += '</div>'

    # ===== 11. CENTRO DE CUSTOS =====
    html += '<div class="secao"><h2>11. Análise Centro de Custos</h2>'
    if "centro_custos" in modulos:
        d = modulos["centro_custos"].get("dados", {})
        inner = safe(d, "dados", default=d)
        html += '<table><tr><th>Centro de Custo</th><th>Valor</th></tr>'
        for chave, valor in inner.items():
            if isinstance(valor, (str, int, float)):
                html += f'<tr><td>{chave.replace("_"," ").title()}</td><td class="right">{fmt_moeda(valor)}</td></tr>'
        html += '</table>'
    else:
        html += '<div class="status-warn">Módulo não encontrado.</div>'
    html += '</div>'

    # ===== 12. CUSTO DE PESSOAL =====
    html += '<div class="secao"><h2>12. Custo de Pessoal</h2>'
    if "custo_pessoal" in modulos:
        d = modulos["custo_pessoal"].get("dados", {})
        inner = safe(d, "dados", default=d)
        html += '<table><tr><th>Item</th><th>Valor</th></tr>'
        for k, label in [("rcl_total", "RCL Total"), ("pessoal_total", "Pessoal Total"), ("custo_total", "Custo Total"), ("limite_total", "Limite Total"), ("margem_disponivel_total", "Margem Disponível")]:
            if k in inner:
                html += f'<tr><td>{label}</td><td class="right">{fmt_moeda(inner[k])}</td></tr>'
        html += '</table>'
        if "pct_custo_total" in inner:
            html += f'<div class="status-ok"><strong>Percentual de Custo:</strong> {inner["pct_custo_total"]}%</div>'
    else:
        html += '<div class="status-warn">Módulo não encontrado.</div>'
    html += '</div>'

    html += '</body></html>'

    # ===== RENDERIZA VIA PLAYWRIGHT =====
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        page.wait_for_timeout(500)
        pdf_bytes = page.pdf(format="A4", orientation="portrait", print_background=True, margin={"top":"15mm","bottom":"15mm","left":"15mm","right":"15mm"})
        browser.close()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=relatorio_consolidado_{id}.pdf"}
    )
'''

codigo += "\n" + nova_rota

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(codigo)
print("[OK] Nova rota consolidada gerada com HTML único e Playwright (A4 retrato homogêneo).")
