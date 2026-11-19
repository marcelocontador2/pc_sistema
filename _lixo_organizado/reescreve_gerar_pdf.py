import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
linhas = arquivo.read_text(encoding="utf-8").splitlines(keepends=True)

# Encontra a funcao gerar_pdf_relatorio_consolidado
inicio = -1
for i, l in enumerate(linhas):
    if '@app.get("/gerar_pdf_relatorio_consolidado/{id}")' in l:
        inicio = i
        break

if inicio == -1:
    print("[ERRO] Funcao nao encontrada.")
    sys.exit(1)

# Encontra o fim da funcao (proxima linha que comeca com @app ou def em coluna 0)
fim = inicio
for i in range(inicio + 1, len(linhas)):
    if linhas[i].startswith('@app') or linhas[i].startswith('def ') and not linhas[i].startswith('def gerar_pdf'):
        fim = i
        break

print(f"[INFO] Substituindo funcao gerar_pdf (linhas {inicio+1} a {fim})")

# Novo bloco da funcao com acentos corretos e renderizador do DFC/Liquidez
novo_bloco = '''@app.get("/gerar_pdf_relatorio_consolidado/{id}")
def gerar_pdf_relatorio_consolidado(id: int):
    from fastapi.responses import Response
    import json
    import psycopg2
    from playwright.sync_api import sync_playwright
    import os
    import base64
    
    from pc_backend.app.config import PG_CONFIG
    
    def fmt(v):
        if v is None: return "-"
        if isinstance(v, (int, float)):
            return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return str(v)
    
    def pct(v):
        if v is None: return "-"
        return f"{v:+.2f}%".replace(".", ",")
    
    def calc_var(atual, anterior):
        if anterior and anterior != 0:
            return ((atual - anterior) / abs(anterior)) * 100
        return 0.0
    
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_relatorio_consolidado WHERE id = %s", (id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return Response(content="Relatorio nao encontrado", status_code=404)
    
    periodo, data_geracao, resultado_json = row
    dados_consolidados = json.loads(resultado_json)
    
    # Nomes corretos (sem mojibake)
    mapa_tabelas = {
        "Conferencia das Demonstracoes": "1. Conferencia das Demonstracoes",
        "Integridade entre Demonstracoes": "2. Integridade entre Demonstracoes",
        "Analise BP": "3. Analise do Balanco Patrimonial",
        "Analise Orcamentaria (BO)": "4. Analise do Balanco Orcamentario",
        "Analise Financeira (BF)": "5. Analise do Balanco Financeiro",
        "Analise DFC": "6. Analise do Fluxo de Caixa",
        "Analise Patrimonial (DVP)": "7. Analise das Variacoes Patrimoniais",
        "Demonstracao das Mutacoes do PL (DMPL)": "8. Demonstracao das Mutacoes do Patrimonio Liquido (DMPL)",
        "Comparativo de Receitas": "9. Comparativo de Receitas",
        "Comparativo de Despesas": "10. Comparativo de Despesas",
        "Indices de Liquidez": "11. Indices de Liquidez e Estrutura",
        "Panorama de Resultados": "12. Panorama de Resultados",
        "Analise por Centro de Custos": "13. Analise por Centro de Custos",
        "Custo de Pessoal": "14. Custo de Pessoal",
        "DMPl": "8. Demonstracao das Mutacoes do PL (DMPL)"
    }
    
    # Busca os dados no JSON
    encontrados = dados_consolidados.get("dados", [])
    
    # Monta o HTML
    html = """<html><head><meta charset="utf-8"><style>
    body { font-family: Arial, sans-serif; padding: 20px; font-size: 12px; }
    h1 { color: #1a237e; text-align: center; }
    h2 { color: #1a237e; border-bottom: 1px solid #ccc; margin-top: 30px; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background: #f5f5f5; }
    .text-right { text-align: right; }
    .status-ok { color: green; font-weight: bold; }
    </style></head><body>"""
    
    html += f"""<h1>RELATORIO CONSOLIDADO</h1>
    <h2>Analise Contabil - COFEN</h2>
    <p><strong>Periodo:</strong> {periodo}</p>
    <p><strong>Gerado em:</strong> {data_geracao}</p>
    """
    
    for item in encontrados:
        nome = item.get("nome", "")
        dados_item = item.get("dados", {})
        
        # Pega o titulo bonito
        titulo = mapa_tabelas.get(nome, nome)
        html += f"<h2>{titulo}</h2>"
        
        # ===== MODULO 6: DFC (Fluxo de Caixa) =====
        if "DFC" in nome or "Fluxo de Caixa" in nome:
            if "operacional" in dados_item or "investimento" in dados_item or "financiamento" in dados_item:
                html += "<table><thead><tr><th>Grupo</th><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>"
                for grupo_nome in ["operacional", "investimento", "financiamento"]:
                    grupo = dados_item.get(grupo_nome, {})
                    for k, v in grupo.items():
                        if isinstance(v, dict):
                            a = v.get("atual", 0)
                            ant = v.get("anterior", 0)
                            var = calc_var(a, ant)
                            html += f"<tr><td>{grupo_nome.capitalize()}</td><td>{k.title()}</td><td class='text-right'>{fmt(a)}</td><td class='text-right'>{fmt(ant)}</td><td class='text-right'>{pct(var)}</td></tr>"
                html += "</tbody></table>"
            else:
                html += "<p>Sem dados de fluxo de caixa para este periodo.</p>"
            continue
        
        # ===== MODULO 11: LIQUIDEZ =====
        if "Liquidez" in nome or "ndices de Liquidez" in nome:
            html += "<table><thead><tr><th>Indicador</th><th>Atual</th><th>Anterior</th><th>Variacao</th></tr></thead><tbody>"
            
            liq_atual = dados_item.get("liquidez", {})
            liq_ant = dados_item.get("liquidez_anterior", {})
            est_atual = dados_item.get("estrutura", {})
            est_ant = dados_item.get("estrutura_anterior", {})
            
            # Tabela de Liquidez
            html += "<tr><th colspan='4' style='background:#e3f2fd'>LIQUIDEZ</th></tr>"
            for k in ["liquidez_imediata", "liquidez_corrente", "liquidez_seca", "liquidez_geral"]:
                va = liq_atual.get(k, "-")
                vb = liq_ant.get(k, "-")
                html += f"<tr><td>{k.replace('_', ' ').title()}</td><td>{va}</td><td>{vb}</td><td>-</td></tr>"
            
            # Tabela de Estrutura
            html += "<tr><th colspan='4' style='background:#e3f2fd'>ESTRUTURA</th></tr>"
            for k in ["endividamento_geral", "part_capital_terceiros", "imobilizacao_pl"]:
                va = est_atual.get(k, "-")
                vb = est_ant.get(k, "-")
                html += f"<tr><td>{k.replace('_', ' ').title()}</td><td>{va}</td><td>{vb}</td><td>-</td></tr>"
            
            html += "</tbody></table>"
            continue
        
        # ===== OUTROS MODULOS (generico) =====
        if isinstance(dados_item, dict) and dados_item.get("analises"):
            for analise in dados_item["analises"]:
                html += f"<h3>{analise.get('titulo', '')}</h3>"
                html += f"<p>{analise.get('conceito', '')}</p>"
                if analise.get("tabela"):
                    html += "<table><tbody>"
                    for t in analise["tabela"]:
                        html += f"<tr><td>{t.get('label')}</td><td>{t.get('valor')}</td></tr>"
                    html += "</tbody></table>"
                html += f"<p class='status-ok'>{analise.get('status', '')} - {analise.get('mensagem', '')}</p>"
        else:
            html += f"<p>Modulo sem mapeamento especifico.</p>"
    
    html += "</body></html>"
    
    # Renderiza com Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html)
        pdf_bytes = page.pdf(format="A4", print_background=True)
        browser.close()
    
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=relatorio_consolidado_{periodo}.pdf"})

'''

linhas[inicio:fim] = [novo_bloco]
arquivo.write_text("".join(linhas), encoding="utf-8")
print("[OK] Funcao gerar_pdf reescrita com sucesso!")
