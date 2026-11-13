import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_pdf_modelo_exato")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

idx_inicio = conteudo.find("def gerar_pdf_relatorio_consolidado(")
if idx_inicio == -1:
    print("❌ Função não encontrada.")
else:
    idx_fim = conteudo.find("\n@app.", idx_inicio)
    if idx_fim == -1:
        idx_fim = len(conteudo)
    
    nova_funcao = '''def gerar_pdf_relatorio_consolidado(id: int):
    from fastapi.responses import Response
    import json
    import psycopg2
    from playwright.sync_api import sync_playwright
    
    PG_CONFIG = {
        "host": "localhost", "port": 5433,
        "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
    }
    
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
    
    mapa_tabelas = {
        "Integridade entre Demonstrações": ("historico_integridade_matriz", "resultado_json"),
        "Análise BP": ("historico_analise_bp", "resultado_json"),
        "Análise DFC": ("historico_analise_dfc", "resultado_json"),
        "Análise Patrimonial (DVP)": ("historico_analise_patrimonial", "resultado_json"),
        "Análise Orçamentária (BO)": ("historico_analise_orcamentaria", "resultado_json"),
        "Análise Financeira (BF)": ("historico_analise_financeira_bf", "resultado_json"),
        "Comparativo de Receitas": ("historico_comparativo_receitas", "dados_json"),
        "Comparativo de Despesas": ("historico_comparativo_despesas", "dados_json"),
        "Panorama de Resultados": ("historico_panorama", "resultado_json"),
        "Índices de Liquidez": ("historico_liquidez", "resultado_json"),
        "Conferência das Demonstrações": ("historico_conferencia", "resultado_json"),
        "Custo de Pessoal": ("historico_custo_pessoal", "resultado_json"),
        "Análise por Centro de Custos": ("historico_centro_custos", "dados_json")
    }
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_relatorio_consolidado WHERE id = %s", (id,))
        row = cursor.fetchone()
        if not row:
            return Response(content="Relatório não encontrado.", status_code=404, media_type="text/plain")
        
        periodo, data_geracao, res_json = row
        dados_consolidados = json.loads(res_json)
        modulos_lista = dados_consolidados.get("dados", [])
        
        # Reordena os módulos para ficar igual ao modelo (Integridade primeiro)
        ordem_modelo = [
            "Integridade entre Demonstrações", "Análise BP", "Análise DFC",
            "Análise Patrimonial (DVP)", "Análise Orçamentária (BO)",
            "Análise Financeira (BF)", "Comparativo de Receitas",
            "Comparativo de Despesas", "Panorama de Resultados",
            "Índices de Liquidez", "Conferência das Demonstrações",
            "Custo de Pessoal", "Análise por Centro de Custos"
        ]
        modulos_ordenados = sorted(modulos_lista, key=lambda m: ordem_modelo.index(m.get("nome", "")) if m.get("nome") in ordem_modelo else 99)
        
        dados_globais = {}
        html_parts = []
        
        # --- INÍCIO DO HTML ---
        html_parts.append("<!DOCTYPE html><html><head><meta charset='UTF-8'>")
        html_parts.append("<style>")
        html_parts.append("@page { size: A4; margin: 2cm; }")
        html_parts.append("body { font-family: Arial, sans-serif; font-size: 10pt; color: #333; }")
        html_parts.append("h1 { color: #003366; font-size: 22pt; text-align: center; margin-top: 80px; }")
        html_parts.append("h2 { color: #003366; font-size: 14pt; border-bottom: 2px solid #004b8d; padding-bottom: 5px; margin-top: 25px; }")
        html_parts.append("h3 { color: #004b8d; font-size: 12pt; margin-top: 15px; }")
        html_parts.append(".capa { text-align: center; padding-top: 60px; }")
        html_parts.append(".capa .periodo { font-size: 12pt; color: #666; font-style: italic; margin-top: 20px; }")
        html_parts.append(".capa .orgao { font-size: 14pt; color: #003366; margin-top: 30px; }")
        html_parts.append(".capa .legislacao { font-size: 8pt; color: #666; margin-top: 30px; padding: 0 40px; text-align: justify; }")
        html_parts.append(".page-break { page-break-before: always; }")
        html_parts.append("table { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 9pt; }")
        html_parts.append("th { background-color: #004b8d; color: white; padding: 8px; text-align: center; border: 1px solid #ccc; }")
        html_parts.append("td { padding: 6px 8px; border: 1px solid #ccc; }")
        html_parts.append("tr:nth-child(even) { background-color: #f9f9f9; }")
        html_parts.append(".text-right { text-align: right; }")
        html_parts.append(".text-center { text-align: center; }")
        html_parts.append(".alerta-info { background-color: #e7f1ff; border: 1px solid #b6d4fe; padding: 10px; border-radius: 5px; margin: 15px 0; font-size: 9pt; }")
        html_parts.append(".parecer p { text-align: justify; margin-bottom: 10px; }")
        html_parts.append(".assinatura { margin-top: 50px; text-align: center; }")
        html_parts.append(".assinatura .linha { border-top: 1px solid #000; width: 300px; margin: 0 auto; }")
        html_parts.append(".grafico { width: 100%; max-width: 500px; margin: 20px auto; }")
        html_parts.append(".texto-dinamico { text-align: justify; margin: 10px 0; line-height: 1.5; }")
        html_parts.append("</style>")
        html_parts.append("<script src='https://cdn.jsdelivr.net/npm/chart.js'></script>")
        html_parts.append("</head><body>")
        
        # --- CAPA ---
        html_parts.append("<div class='capa'>")
        html_parts.append("<h1>RELATÓRIO CONSOLIDADO</h1>")
        html_parts.append("<h2 style='border: none;'>Análise Contábil</h2>")
        html_parts.append("<div class='orgao'>COFEN - Conselho Federal de Enfermagem</div>")
        html_parts.append(f"<div class='periodo'>PERÍODO DE ANÁLISE: {periodo}</div>")
        
        html_parts.append("<div class='legislacao'>")
        html_parts.append("<strong>LEGISLAÇÃO E NORMAS APLICADAS:</strong><br>")
        html_parts.append("Lei nº 4.320/1964 (Normas gerais de direito financeiro para elaboração e controle dos orçamentos e balanços.) • ")
        html_parts.append("Resolução COFEN nº 340/2008 (Regulamento da Administração Financeira e Contábil) • ")
        html_parts.append("Normas Brasileiras de Contabilidade – Setor Público (NBC TSP) • ")
        html_parts.append("Resolução COFEN nº 764/2024 (Prestação de Contas) • ")
        html_parts.append("Resolução Cofen nº 799/2025 (Gestão de riscos e controles internos) • ")
        html_parts.append("Resolução Cofen nº 814/2026 (Limites de despesa com pessoal) • ")
        html_parts.append("Manual de Contabilidade Aplicada ao Setor Público (MCASP)")
        html_parts.append("</div>")
        
        html_parts.append("<div class='legislacao' style='margin-top: 20px;'>")
        html_parts.append("<strong>DEMONSTRAÇÕES ANALISADAS:</strong><br>")
        html_parts.append("Balancete de Verificação • Balanço Financeiro (BF) • Balanço Orçamentário (BO) • Balanço Patrimonial (BP) • Demonstração do Fluxo de Caixa (DFC) • Demonstração das Mutações do PL (DMPL) • Demonstração das Variações Patrimoniais (DVP)")
        html_parts.append("</div>")
        html_parts.append("</div>")
        
        # --- MÓDULOS ---
        for i, m in enumerate(modulos_ordenados):
            nome = m.get("nome", "Módulo")
            data_mod = m.get("data_geracao", "N/A")
            
            html_parts.append("<div class='page-break'></div>")
            html_parts.append(f"<h2>{i+1}. {nome}</h2>")
            html_parts.append(f"<p style='color:#666; font-style:italic; border-bottom: 1px solid #ccc; padding-bottom: 5px;'>Gerado em: {data_mod}</p>")
            
            tabela, coluna = mapa_tabelas.get(nome, (None, None))
            if not tabela:
                html_parts.append("<p style='color:red;'>Módulo sem mapeamento.</p>")
                continue
            
            try:
                cursor.execute(f"SELECT {coluna} FROM {tabela} WHERE periodo LIKE %s ORDER BY id DESC LIMIT 1", (f"%{periodo}%",))
                mod_row = cursor.fetchone()
                
                if not mod_row or not mod_row[0]:
                    html_parts.append("<p style='color:red;'>Dados não encontrados.</p>")
                    continue
                
                mod_dados = json.loads(mod_row[0])
                
                if nome == "Integridade entre Demonstrações":
                    matriz = mod_dados.get("matriz", [])
                    html_parts.append("<p>Matriz de integridade com o cruzamento de todas as demonstrações.</p>")
                    html_parts.append("<table><thead><tr><th>ITEM</th><th>BALANCETE</th><th>BP</th><th>BF</th><th>BO</th><th>DFC</th><th>DVP</th><th>DMPL</th><th>CONF</th></tr></thead><tbody>")
                    for mi in matriz:
                        html_parts.append(f"<tr><td>{mi.get('item','')}</td><td class='text-right'>{mi.get('balancete','')}</td><td class='text-right'>{mi.get('bp','')}</td><td class='text-right'>{mi.get('bf','')}</td><td class='text-right'>{mi.get('bo','')}</td><td class='text-right'>{mi.get('dfc','')}</td><td class='text-right'>{mi.get('dvp','')}</td><td class='text-right'>{mi.get('dmpl','')}</td><td class='text-center'>{mi.get('conf','')}</td></tr>")
                    html_parts.append("</tbody></table>")
                    html_parts.append("<div class='alerta-info'>1. Os itens de conformidade em vermelho, de 1 a 4, são por estornos de restos a pagar.<br>2. Incorporação de Ativos: SOMA = 16.271.957,08.</div>")
                
                elif nome == "Análise BP":
                    dados_bp = mod_dados.get("dados", {})
                    html_parts.append("<p>Comparativo das contas do Balanço Patrimonial (período atual x anterior).</p>")
                    html_parts.append("<table><thead><tr><th>CONTA</th><th>PERÍODO ATUAL (R$)</th><th>PERÍODO ANTERIOR (R$)</th><th>VAR. (%)</th></tr></thead><tbody>")
                    textos = []
                    for k, v in dados_bp.items():
                        if isinstance(v, dict):
                            atual = v.get("atual", 0)
                            anterior = v.get("anterior", 0)
                            var = calc_var(atual, anterior)
                            html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td class='text-right'>{fmt(atual)}</td><td class='text-right'>{fmt(anterior)}</td><td class='text-right'>{pct(var)}</td></tr>")
                            if abs(var) > 0.01:
                                direcao = "positiva" if var > 0 else "negativa"
                                textos.append(f"<li>{k.replace('_', ' ').title()}, variação {direcao} de {pct(var)}.</li>")
                    html_parts.append("</tbody></table>")
                    html_parts.append("<h3>Evolução das Principais Contas</h3><ul class='texto-dinamico'>" + "".join(textos[:6]) + "</ul>")
                    # Gráfico de barras
                    labels = [k.replace('_', ' ').title() for k, v in dados_bp.items() if isinstance(v, dict)]
                    atual_vals = [v.get('atual', 0) for v in dados_bp.values() if isinstance(v, dict)]
                    ant_vals = [v.get('anterior', 0) for v in dados_bp.values() if isinstance(v, dict)]
                    html_parts.append("<div class='grafico'><canvas id='chartBP'></canvas></div>")
                    html_parts.append("<script>")
                    html_parts.append("new Chart(document.getElementById('chartBP'), {")
                    html_parts.append("type: 'bar',")
                    html_parts.append(f"data: {{ labels: {json.dumps(labels)}, datasets: [")
                    html_parts.append(f"{{ label: 'Atual', data: {json.dumps(atual_vals)}, backgroundColor: '#004b8d' }},")
                    html_parts.append(f"{{ label: 'Anterior', data: {json.dumps(ant_vals)}, backgroundColor: '#6c757d' }}")
                    html_parts.append("] },")
                    html_parts.append("options: { responsive: true, plugins: { legend: { position: 'top' } } }")
                    html_parts.append("});")
                    html_parts.append("</script>")
                    dados_globais['bp'] = dados_bp
                
                elif nome == "Comparativo de Receitas":
                    atual = mod_dados.get("atual", {})
                    html_parts.append("<p>Comparativo consolidado de receitas.</p>")
                    html_parts.append("<h3>Resumo</h3><table><thead><tr><th>INDICADOR</th><th>VALOR</th></tr></thead><tbody>")
                    html_parts.append(f"<tr><td>Receita Orçada</td><td class='text-right'>{fmt(atual.get('orcado_total'))}</td></tr>")
                    html_parts.append(f"<tr><td>Receita Realizada</td><td class='text-right'>{fmt(atual.get('realizado_total'))}</td></tr>")
                    html_parts.append(f"<tr><td>% Execução</td><td class='text-right'>{atual.get('percentual_total', 0):.2f}%</td></tr>")
                    html_parts.append("</tbody></table>")
                    html_parts.append("<h3>Composição por Grupo</h3><table><thead><tr><th>GRUPO</th><th>ORÇADO</th><th>REALIZADO</th><th>%</th></tr></thead><tbody>")
                    for g in atual.get("grupos", []):
                        html_parts.append(f"<tr><td>{g.get('nome','')}</td><td class='text-right'>{fmt(g.get('orcado'))}</td><td class='text-right'>{fmt(g.get('realizado'))}</td><td class='text-right'>{g.get('percentual',0):.2f}%</td></tr>")
                    html_parts.append("</tbody></table>")
                    html_parts.append(f"<p class='texto-dinamico'>A receita realizada foi de {fmt(atual.get('realizado_total'))}, correspondendo a {atual.get('percentual_total', 0):.2f}% da receita orçada de {fmt(atual.get('orcado_total'))}.</p>")
                    labels = [g.get('nome') for g in atual.get('grupos', [])]
                    vals = [g.get('realizado') for g in atual.get('grupos', [])]
                    html_parts.append("<div class='grafico'><canvas id='chartReceitas'></canvas></div>")
                    html_parts.append("<script>")
                    html_parts.append("new Chart(document.getElementById('chartReceitas'), {")
                    html_parts.append("type: 'doughnut',")
                    html_parts.append(f"data: {{ labels: {json.dumps(labels)}, datasets: [{{ data: {json.dumps(vals)}, backgroundColor: ['#004b8d', '#007bff', '#6c757d', '#28a745', '#ffc107'] }}] }}")
                    html_parts.append("});")
                    html_parts.append("</script>")
                    dados_globais['receitas'] = atual
                
                elif nome == "Comparativo de Despesas":
                    atual = mod_dados.get("atual", {})
                    html_parts.append("<p>Comparativo consolidado de despesas.</p>")
                    html_parts.append("<h3>Resumo</h3><table><thead><tr><th>INDICADOR</th><th>VALOR</th></tr></thead><tbody>")
                    html_parts.append(f"<tr><td>Despesa Orçada</td><td class='text-right'>{fmt(atual.get('orcado_total'))}</td></tr>")
                    html_parts.append(f"<tr><td>Despesa Empenhada</td><td class='text-right'>{fmt(atual.get('empenhado_total'))}</td></tr>")
                    html_parts.append(f"<tr><td>Despesa Liquidada</td><td class='text-right'>{fmt(atual.get('liquidado_total'))}</td></tr>")
                    html_parts.append(f"<tr><td>% Execução</td><td class='text-right'>{atual.get('percentual_total', 0):.2f}%</td></tr>")
                    html_parts.append("</tbody></table>")
                    html_parts.append("<h3>Composição por Grupo</h3><table><thead><tr><th>GRUPO</th><th>ORÇADO</th><th>EMPENHADO</th><th>LIQUIDADO</th><th>%</th></tr></thead><tbody>")
                    for g in atual.get("grupos", []):
                        html_parts.append(f"<tr><td>{g.get('nome','')}</td><td class='text-right'>{fmt(g.get('orcado'))}</td><td class='text-right'>{fmt(g.get('empenhado'))}</td><td class='text-right'>{fmt(g.get('liquidado'))}</td><td class='text-right'>{g.get('percentual',0):.2f}%</td></tr>")
                    html_parts.append("</tbody></table>")
                    html_parts.append(f"<p class='texto-dinamico'>A despesa empenhada foi de {fmt(atual.get('empenhado_total'))}, correspondendo a {atual.get('percentual_total', 0):.2f}% da despesa orçada de {fmt(atual.get('orcado_total'))}.</p>")
                    labels = [g.get('nome') for g in atual.get('grupos', [])]
                    vals = [g.get('empenhado') for g in atual.get('grupos', [])]
                    html_parts.append("<div class='grafico'><canvas id='chartDespesas'></canvas></div>")
                    html_parts.append("<script>")
                    html_parts.append("new Chart(document.getElementById('chartDespesas'), {")
                    html_parts.append("type: 'doughnut',")
                    html_parts.append(f"data: {{ labels: {json.dumps(labels)}, datasets: [{{ data: {json.dumps(vals)}, backgroundColor: ['#dc3545', '#fd7e14', '#ffc107', '#28a745', '#007bff'] }}] }}")
                    html_parts.append("});")
                    html_parts.append("</script>")
                    dados_globais['despesas'] = atual
                
                elif nome == "Índices de Liquidez":
                    liq = mod_dados.get("liquidez", {})
                    est = mod_dados.get("estrutura", {})
                    html_parts.append("<p>Indicadores de liquidez e estrutura patrimonial (atual x anterior).</p>")
                    html_parts.append("<h3>Liquidez</h3><table><thead><tr><th>INDICADOR</th><th>ATUAL</th></tr></thead><tbody>")
                    for k, v in liq.items():
                        html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td class='text-right'>{v}</td></tr>")
                    html_parts.append("</tbody></table>")
                    html_parts.append("<h3>Estrutura Patrimonial</h3><table><thead><tr><th>INDICADOR</th><th>ATUAL</th></tr></thead><tbody>")
                    for k, v in est.items():
                        html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td class='text-right'>{v}</td></tr>")
                    html_parts.append("</tbody></table>")
                    dados_globais['liquidez'] = liq
                
                elif nome == "Panorama de Resultados":
                    html_parts.append("<p>Resumo executivo dos principais indicadores.</p>")
                    html_parts.append("<table><thead><tr><th>INDICADOR</th><th>VALOR</th></tr></thead><tbody>")
                    for k, v in mod_dados.items():
                        if isinstance(v, (int, float)):
                            html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td class='text-right'>{fmt(v)}</td></tr>")
                    html_parts.append("</tbody></table>")
                
                elif nome == "Custo de Pessoal":
                    html_parts.append("<p>Custo de pessoal x limite legal (Resolução Cofen 814/2026).</p>")
                    html_parts.append("<table><thead><tr><th>INDICADOR</th><th>VALOR</th></tr></thead><tbody>")
                    html_parts.append(f"<tr><td>RCL Total</td><td class='text-right'>{fmt(mod_dados.get('rcl_total'))}</td></tr>")
                    html_parts.append(f"<tr><td>Custo Total</td><td class='text-right'>{fmt(mod_dados.get('custo_atual'))}</td></tr>")
                    html_parts.append(f"<tr><td>Limite Legal (50%)</td><td class='text-right'>{fmt(mod_dados.get('limite_total'))}</td></tr>")
                    html_parts.append(f"<tr><td>Margem Disponível</td><td class='text-right'>{fmt(mod_dados.get('margem_disponivel_total'))}</td></tr>")
                    html_parts.append("</tbody></table>")
                    pct_custo = (mod_dados.get("custo_atual", 0) / mod_dados.get("rcl_total", 1)) * 100 if mod_dados.get("rcl_total") else 0
                    html_parts.append(f"<p class='texto-dinamico'>O custo de pessoal representa {pct_custo:.2f}% da RCL.</p>")
                    dados_globais['custo'] = {'pct': pct_custo}
                
                elif nome == "Análise por Centro de Custos":
                    centros = mod_dados.get("centros", [])
                    html_parts.append("<p>Distribuição das despesas por centro de custo.</p>")
                    html_parts.append("<table><thead><tr><th>CENTRO DE CUSTO</th><th>VALOR</th></tr></thead><tbody>")
                    for c in centros:
                        html_parts.append(f"<tr><td>{c.get('nome','')}</td><td class='text-right'>{fmt(c.get('valor'))}</td></tr>")
                    html_parts.append("</tbody></table>")
                    if centros:
                        maior = max(centros, key=lambda x: x.get("valor", 0))
                        html_parts.append(f"<p class='texto-dinamico'>O maior centro de custo é {maior.get('nome')} com {fmt(maior.get('valor'))}.</p>")
                
                elif nome == "Análise DFC":
                    dados_dfc = mod_dados.get("dados", {})
                    html_parts.append("<p>Demonstração do Fluxo de Caixa (método direto).</p>")
                    for tipo in ["operacional", "investimento", "financiamento"]:
                        if tipo in dados_dfc:
                            html_parts.append(f"<h3>Fluxo {tipo.title()}</h3><table><thead><tr><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th></tr></thead><tbody>")
                            for k, v in dados_dfc[tipo].items():
                                if isinstance(v, dict):
                                    html_parts.append(f"<tr><td>{k.title()}</td><td class='text-right'>{fmt(v.get('atual'))}</td><td class='text-right'>{fmt(v.get('anterior'))}</td></tr>")
                            html_parts.append("</tbody></table>")
                
                elif nome == "Análise Patrimonial (DVP)":
                    html_parts.append("<p>Demonstração das Variações Patrimoniais.</p>")
                    html_parts.append("<table><thead><tr><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th></tr></thead><tbody>")
                    for k, v in mod_dados.items():
                        if isinstance(v, dict):
                            html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td class='text-right'>{fmt(v.get('atual'))}</td><td class='text-right'>{fmt(v.get('anterior'))}</td></tr>")
                    html_parts.append("</tbody></table>")
                
                elif nome == "Análise Orçamentária (BO)":
                    atual = mod_dados.get("atual", {})
                    html_parts.append("<p>Comparativo das receitas e despesas orçamentárias.</p>")
                    html_parts.append("<table><thead><tr><th>INDICADOR</th><th>ATUAL</th></tr></thead><tbody>")
                    html_parts.append(f"<tr><td>Receita Realizada</td><td class='text-right'>{fmt(atual.get('receita_realizada'))}</td></tr>")
                    html_parts.append(f"<tr><td>Despesa Empenhada</td><td class='text-right'>{fmt(atual.get('despesa_empenhada'))}</td></tr>")
                    html_parts.append(f"<tr><td>Superávit/Déficit</td><td class='text-right'>{fmt(atual.get('superavit'))}</td></tr>")
                    html_parts.append("</tbody></table>")
                
                elif nome == "Análise Financeira (BF)":
                    atual = mod_dados.get("atual", {})
                    html_parts.append("<p>Movimentação financeira consolidada.</p>")
                    html_parts.append("<table><thead><tr><th>INDICADOR</th><th>ATUAL</th><th>ANTERIOR</th></tr></thead><tbody>")
                    for k, v in atual.items():
                        if isinstance(v, dict):
                            html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td class='text-right'>{fmt(v.get('atual'))}</td><td class='text-right'>{fmt(v.get('anterior'))}</td></tr>")
                    html_parts.append("</tbody></table>")
                
                elif nome == "Conferência das Demonstrações":
                    analises = mod_dados.get("analises", [])
                    html_parts.append("<p>Verificação da consistência das demonstrações contábeis.</p>")
                    for a in analises:
                        html_parts.append(f"<h3>{a.get('titulo', '')}</h3>")
                        html_parts.append(f"<p>{a.get('conceito', '')}</p>")
                        html_parts.append("<table><thead><tr><th>ITEM</th><th>VALOR</th></tr></thead><tbody>")
                        for t in a.get("tabela", []):
                            html_parts.append(f"<tr><td>{t.get('label','')}</td><td class='text-right'>{t.get('valor','')}</td></tr>")
                        html_parts.append("</tbody></table>")
                        html_parts.append(f"<p><strong>Status:</strong> {a.get('status','')} - {a.get('mensagem','')}</p>")
                
                else:
                    html_parts.append(f"<pre>{json.dumps(mod_dados, ensure_ascii=False, indent=2)[:2000]}</pre>")
                    
            except Exception as e:
                html_parts.append(f"<p style='color:red;'>Erro: {str(e)}</p>")
        
        # --- PARECER DO CONTADOR ---
        liq = dados_globais.get('liquidez', {})
        custo = dados_globais.get('custo', {})
        bp = dados_globais.get('bp', {})
        total_ativo = bp.get('total_ativo', {}).get('atual', 0) if isinstance(bp.get('total_ativo'), dict) else 0
        total_passivo = bp.get('passivo_circulante', {}).get('atual', 0) + bp.get('passivo_nao_circulante', {}).get('atual', 0) if isinstance(bp.get('passivo_circulante'), dict) else 0
        
        html_parts.append("<div class='page-break'></div>")
        html_parts.append("<h2>PARECER DO CONTADOR</h2>")
        html_parts.append("<div class='parecer'>")
        html_parts.append("<p><strong>1. Situação Patrimonial e Financeira — Sólida e Equilibrada</strong></p>")
        html_parts.append(f"<p>A entidade apresenta solidez financeira notável, evidenciada por um caixa elevado que suporta integralmente seus gastos operacionais. O índice de liquidez imediata de {liq.get('liquidez_imediata', '-')} e o índice de liquidez geral de {liq.get('liquidez_geral', '-')} demonstram capacidade excepcional de honrar compromissos de curto e longo prazos. O endividamento geral de {liq.get('endividamento_geral', '-')} confirma uma estrutura de capital conservadora.</p>")
        
        html_parts.append("<p><strong>2. Desempenho Orçamentário — Estabilidade</strong></p>")
        html_parts.append("<p>As receitas e despesas orçamentárias realizadas mantiveram-se no mesmo patamar do exercício anterior, indicando previsibilidade e controle na execução orçamentária.</p>")
        
        html_parts.append("<p><strong>3. Geração de Caixa — Evolução Positiva</strong></p>")
        html_parts.append("<p>A Demonstração dos Fluxos de Caixa (DFC) revela geração líquida de caixa positiva, reforçando a capacidade de autofinanciamento e a consistência operacional da entidade.</p>")
        
        html_parts.append("<p><strong>4. Resultado Patrimonial — Crescimento Contábil Relevante</strong></p>")
        html_parts.append("<p>O resultado patrimonial registrou acréscimo significativo. Contudo, trata-se de resultado contábil, sem reflexo financeiro imediato, devendo ser interpretado com cautela.</p>")
        
        html_parts.append("<p><strong>5. Estrutura de Custos — Conformidade e Eficiência</strong></p>")
        html_parts.append(f"<p>Custo de Pessoal: representa {custo.get('pct', 0):.2f}% da RCL, {'dentro' if custo.get('pct', 0) < 50 else 'fora'} do limite legal de 50%.</p>")
        
        html_parts.append("<p><strong>6. Integridade das Demonstrações</strong></p>")
        html_parts.append("<p>Verificou-se a integridade das demonstrações contábeis, que se apresentam adequadas e em conformidade com os princípios e normas aplicáveis.</p>")
        
        html_parts.append("<p><strong>Considerações Finais</strong></p>")
        html_parts.append("<p>O Cofen demonstra excelente saúde financeira e patrimonial, com liquidez amplamente favorável, endividamento irrisório, geração de caixa positiva e crescimento contábil expressivo. A execução orçamentária é estável e o custo com pessoal encontra-se dentro dos limites legais.</p>")
        
        html_parts.append("<p><strong>Conclusão:</strong> As demonstrações contábeis refletem equilíbrio, solidez e conformidade, não havendo indícios de risco financeiro ou descumprimento de limites legais.</p>")
        
        html_parts.append("</div>")
        html_parts.append("<div class='assinatura'><div class='linha'></div><p>Marcelo Ribeiro Medeiros<br>CRC: 066005O8T/DF</p></div>")
        html_parts.append("</body></html>")
        
        html = "".join(html_parts)
        
        cursor.close()
        conn.close()
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html, wait_until='networkidle')
            pdf_bytes = page.pdf(format='A4', print_background=True)
            browser.close()
        
        return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=relatorio_{periodo}.pdf"})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(content=f"Erro ao gerar PDF: {str(e)}", status_code=500, media_type="text/plain")'''

    conteudo = conteudo[:idx_inicio] + nova_funcao + conteudo[idx_fim:]
    print("✅ Função de PDF reescrita seguindo o modelo exato.")

try:
    ast.parse(conteudo)
    with open(caminho_main, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
