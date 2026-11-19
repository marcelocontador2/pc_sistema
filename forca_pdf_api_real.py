import sys
from pathlib import Path
import re

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

# 1. Localiza a funcao gerar_pdf_relatorio_consolidado
inicio = texto.find('def gerar_pdf_relatorio_consolidado(id: int):')
if inicio == -1:
    print("[ERRO] Funcao gerar_pdf nao encontrada.")
    sys.exit(1)

fim = texto.find('\n@app', inicio + 10)
if fim == -1: fim = len(texto)

# 2. Substitui o corpo da funcao inteira
novo_bloco = '''def gerar_pdf_relatorio_consolidado(id: int):
    from fastapi.responses import Response
    import json
    import psycopg2
    from playwright.sync_api import sync_playwright
    from pc_backend.app.config import PG_CONFIG
    import asyncio
    
    # 1. Pega o periodo do banco (apenas para saber qual periodo carregar)
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo FROM historico_relatorio_consolidado WHERE id = %s", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return Response(content="Relatorio nao encontrado", status_code=404)
    periodo = row[0]
    
    # Normaliza o periodo (para garantir)
    periodo_norm = str(periodo).replace("TRIMESTRAL", "TRIMESTRE").replace("trimestral", "TRIMESTRE")
    if "TRIMESTRE" in periodo_norm.upper():
        partes = periodo_norm.upper().split("-")
        if len(partes) == 3:
            periodo_norm = f"{partes[0]}-TRIMESTRE-{partes[2]}"
    
    # 2. Busca os dados DIRETO DA API (que ja esta corrigida e retorna os dados)
    dados_consolidados = asyncio.run(api_relatorio_consolidado_novo(periodo_norm))
    encontrados = dados_consolidados.get("encontrados", [])
    
    def fmt(v):
        if v is None: return "-"
        if isinstance(v, (int, float)):
            return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return str(v)
    
    def calc_var(atual, anterior):
        if anterior and anterior != 0:
            return ((atual - anterior) / abs(anterior)) * 100
        return 0.0
    
    # Mapeamento de titulos
    mapa_titulos = {
        "Conferência das Demonstrações": "1. Conferência das Demonstrações",
        "Integridade entre Demonstrações": "2. Integridade entre Demonstrações",
        "Análise BP": "3. Análise do Balanço Patrimonial",
        "Análise Orçamentária (BO)": "4. Análise do Balanço Orçamentário",
        "Análise Financeira (BF)": "5. Análise do Balanço Financeiro",
        "Análise DFC": "6. Análise do Fluxo de Caixa",
        "Análise Patrimonial (DVP)": "7. Análise das Variações Patrimoniais",
        "Demonstração das Mutações do PL (DMPL)": "8. Demonstração das Mutações do PL (DMPL)",
        "Comparativo de Receitas": "9. Comparativo de Receitas",
        "Comparativo de Despesas": "10. Comparativo de Despesas",
        "Índices de Liquidez": "11. Índices de Liquidez e Estrutura",
        "Panorama de Resultados": "12. Panorama de Resultados",
        "Análise por Centro de Custos": "13. Análise por Centro de Custos",
        "Custo de Pessoal": "14. Custo de Pessoal"
    }
    
    html = """<html><head><meta charset="utf-8"><style>
    body { font-family: Arial, sans-serif; padding: 20px; font-size: 12px; }
    h1 { color: #1a237e; text-align: center; }
    h2 { color: #1a237e; border-bottom: 1px solid #ccc; margin-top: 30px; }
    h3 { color: #333; margin-top: 20px; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background: #f5f5f5; }
    .text-right { text-align: right; }
    .json-box { background: #f9f9f9; padding: 10px; border: 1px solid #ddd; font-family: monospace; font-size: 10px; white-space: pre-wrap; }
    </style></head><body>"""
    
    html += f"""<h1>RELATÓRIO CONSOLIDADO</h1>
    <h2>Análise Contábil - COFEN</h2>
    <p><strong>Período:</strong> {periodo_norm}</p>
    <p><strong>Gerado em:</strong> {__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
    """
    
    for item in encontrados:
        nome = item.get("nome", "")
        dados_item = item.get("dados", {})
        titulo = mapa_titulos.get(nome, nome)
        html += f"<h2>{titulo}</h2>"
        
        # --- DFC (ITEM 6) ---
        if "DFC" in nome or "Fluxo de Caixa" in nome:
            dfc_data = dados_item.get("dados", dados_item) if isinstance(dados_item, dict) and "dados" in dados_item else dados_item
            grupos = ["operacional", "investimento", "financiamento"]
            tem_dados = any(g in dfc_data for g in grupos)
            if tem_dados:
                for g in grupos:
                    grupo = dfc_data.get(g, {})
                    if grupo:
                        html += f"<h3>Fluxo {g.capitalize()}</h3><table><thead><tr><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>"
                        for k, v in grupo.items():
                            if isinstance(v, dict):
                                a = v.get("atual", 0)
                                ant = v.get("anterior", 0)
                                var = calc_var(a, ant)
                                html += f"<tr><td>{k.title()}</td><td class='text-right'>{fmt(a)}</td><td class='text-right'>{fmt(ant)}</td><td class='text-right'>{var:+.2f}%</td></tr>"
                        html += "</tbody></table>"
                if "caixa" in dfc_data:
                    html += "<h3>Apuração de Caixa</h3><table><thead><tr><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>"
                    for k, v in dfc_data["caixa"].items():
                        if isinstance(v, dict):
                            a = v.get("atual", 0)
                            ant = v.get("anterior", 0)
                            var = calc_var(a, ant)
                            html += f"<tr><td>{k.title()}</td><td class='text-right'>{fmt(a)}</td><td class='text-right'>{fmt(ant)}</td><td class='text-right'>{var:+.2f}%</td></tr>"
                    html += "</tbody></table>"
            else:
                html += "<p>Sem dados de fluxo de caixa.</p>"
            continue
        
        # --- LIQUIDEZ (ITEM 11) ---
        if "Liquidez" in nome or "ndices" in nome:
            base = dados_item.get("dados", dados_item) if isinstance(dados_item, dict) and "dados" in dados_item else dados_item
            html += "<table><thead><tr><th>Indicador</th><th>Atual</th><th>Anterior</th></tr></thead><tbody>"
            liq = base.get("liquidez", {})
            liq_ant = base.get("liquidez_anterior", {})
            est = base.get("estrutura", {})
            est_ant = base.get("estrutura_anterior", {})
            
            html += "<tr><th colspan='3' style='background:#e3f2fd'>LIQUIDEZ</th></tr>"
            for k in ["liquidez_imediata", "liquidez_corrente", "liquidez_seca", "liquidez_geral"]:
                html += f"<tr><td>{k.replace('_', ' ').title()}</td><td>{liq.get(k, '-')}</td><td>{liq_ant.get(k, '-')}</td></tr>"
            
            html += "<tr><th colspan='3' style='background:#e3f2fd'>ESTRUTURA</th></tr>"
            for k in ["endividamento_geral", "part_capital_terceiros", "imobilizacao_pl"]:
                html += f"<tr><td>{k.replace('_', ' ').title()}</td><td>{est.get(k, '-')}</td><td>{est_ant.get(k, '-')}</td></tr>"
            
            html += "</tbody></table>"
            continue
        
        # --- OUTROS MODULOS ---
        interno = dados_item.get("dados", dados_item) if isinstance(dados_item, dict) and "dados" in dados_item else dados_item
        if isinstance(interno, dict) and interno.get("analises"):
            for analise in interno["analises"]:
                html += f"<h3>{analise.get('titulo', '')}</h3>"
                html += f"<p>{analise.get('conceito', '')}</p>"
                if analise.get("tabela"):
                    html += "<table><tbody>"
                    for t in analise["tabela"]:
                        html += f"<tr><td>{t.get('label')}</td><td>{t.get('valor')}</td></tr>"
                    html += "</tbody></table>"
                html += f"<p style='color:green;font-weight:bold;'>{analise.get('status', '')} - {analise.get('mensagem', '')}</p>"
        else:
            html += f"<div class='json-box'>{json.dumps(interno, ensure_ascii=False, indent=2)[:1000]}</div>"
    
    html += "</body></html>"
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html)
        pdf_bytes = page.pdf(format="A4", print_background=True)
        browser.close()
    
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=relatorio_consolidado_{periodo_norm}.pdf"})

'''

texto = texto[:inicio] + novo_bloco + texto[fim:]
arquivo.write_text(texto, encoding="utf-8")
print("[OK] Funcao de PDF substituida para buscar dados da API sempre.")
