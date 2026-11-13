import shutil
import ast

# Cria o template HTML em um arquivo separado
template_path = "pc_backend/template_relatorio.html"
with open(template_path, "w", encoding="utf-8") as f:
    f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page { size: A4; margin: 2cm; }
        body { font-family: Arial, sans-serif; color: #333; font-size: 10pt; line-height: 1.4; }
        h1 { color: #003366; font-size: 22pt; text-align: center; margin-bottom: 5px; }
        h2 { color: #003366; font-size: 14pt; border-bottom: 2px solid #004b8d; padding-bottom: 5px; margin-top: 25px; }
        h3 { color: #004b8d; font-size: 12pt; margin-top: 15px; }
        .capa { text-align: center; padding-top: 100px; }
        .capa .periodo { font-size: 12pt; color: #666; font-style: italic; margin-top: 10px; }
        .capa .orgao { font-size: 14pt; color: #003366; margin-top: 30px; }
        .page-break { page-break-before: always; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 9pt; }
        th { background-color: #004b8d; color: white; padding: 8px; text-align: center; border: 1px solid #ccc; }
        td { padding: 6px 8px; border: 1px solid #ccc; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .text-right { text-align: right; }
        .text-center { text-align: center; }
        .alerta { background-color: #fff3cd; border: 1px solid #ffecb5; padding: 10px; border-radius: 5px; margin: 15px 0; }
        .alerta-info { background-color: #e7f1ff; border: 1px solid #b6d4fe; padding: 10px; border-radius: 5px; margin: 15px 0; font-size: 9pt; }
        .parecer { margin-top: 20px; }
        .parecer p { text-align: justify; margin-bottom: 10px; }
        .assinatura { margin-top: 50px; text-align: center; }
        .assinatura .linha { border-top: 1px solid #000; width: 300px; margin: 0 auto; }
        .legislacao { font-size: 8pt; color: #666; margin-top: 20px; }
    </style>
</head>
<body>
    <!-- CAPA -->
    <div class="capa">
        <h1>RELATÓRIO CONSOLIDADO</h1>
        <h2 style="border: none;">Análise Contábil</h2>
        <div class="orgao">COFEN - Conselho Federal de Enfermagem</div>
        <div class="periodo">PERÍODO DE ANÁLISE: {periodo}</div>
        <div class="legislacao">
            <strong>LEGISLAÇÃO E NORMAS APLICADAS:</strong><br>
            Lei nº 4.320/1964 • Resolução COFEN nº 340/2008 • NBC TSP • Resolução COFEN nº 764/2024 • Resolução COFEN nº 799/2025 • Resolução COFEN nº 814/2026 • MCASP
        </div>
    </div>

    <!-- MÓDULOS -->
    {modulos}

    <!-- PARECER -->
    <div class="page-break"></div>
    <h2>PARECER DO CONTADOR</h2>
    <div class="parecer">
        <p>A entidade apresenta solidez financeira notável, evidenciada por um caixa elevado que suporta integralmente seus gastos operacionais. O índice de liquidez imediata de 15,93 e o índice de liquidez geral de 39,74 demonstram capacidade excepcional de honrar compromissos de curto e longo prazos. O endividamento geral de apenas 1,98% confirma uma estrutura de capital extremamente conservadora.</p>
        <p>As receitas e despesas orçamentárias realizadas mantiveram-se no mesmo patamar do exercício anterior, indicando previsibilidade e controle na execução orçamentária.</p>
        <p>A DFC revela geração líquida de caixa de R$ 17 milhões, correspondendo a um crescimento de 19,11% em relação ao período anterior.</p>
        <p>O resultado patrimonial registrou acréscimo significativo de 421%. Contudo, trata-se de resultado contábil, sem reflexo financeiro imediato.</p>
        <p>Custo de Pessoal: R$ 49 milhões, correspondendo a 29,76% do limite legal de 50%, com margem de 20,24% - situação confortável e em conformidade com os limites da Resolução Cofen 814/2026.</p>
        <p>Verificou-se a integridade das demonstrações contábeis, que se apresentam adequadas e em conformidade com os princípios e normas aplicáveis.</p>
        <p>O Cofen demonstra excelente saúde financeira e patrimonial, com liquidez amplamente favorável, endividamento irrisório, geração de caixa positiva e crescimento contábil expressivo. A execução orçamentária é estável e o custo com pessoal encontra-se dentro dos limites legais.</p>
        <p>Recomenda-se: (i) manter o monitoramento dos centros de custo de maior expressão (AF 05); (ii) avaliar a aplicação do caixa elevado em instrumentos que preservem liquidez e rentabilidade; e (iii) acompanhar a natureza do resultado patrimonial para distinguir seus efeitos contábeis dos financeiros.</p>
        <p><strong>Conclusão:</strong> As demonstrações contábeis refletem equilíbrio, solidez e conformidade, não havendo indícios de risco financeiro ou descumprimento de limites legais.</p>
    </div>
    <div class="assinatura">
        <div class="linha"></div>
        <p>Marcelo Ribeiro Medeiros<br>CRC: 066005O8T/DF</p>
    </div>
</body>
</html>""")

print("✅ Template HTML criado em pc_backend/template_relatorio.html")

# --- Substitui a função gerar_pdf_relatorio_consolidado ---
caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_pdf_weasyprint")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

idx_inicio = conteudo.find("def gerar_pdf_relatorio_consolidado(")
if idx_inicio != -1:
    idx_fim = conteudo.find("\n@app.", idx_inicio)
    if idx_fim == -1:
        idx_fim = len(conteudo)
    
    nova_funcao = '''def gerar_pdf_relatorio_consolidado(id: int):
    from fastapi.responses import Response
    import json
    import psycopg2
    from weasyprint import HTML
    import os
    
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
    
    mapa_tabelas = {
        "Análise BP": ("historico_analise_bp", "resultado_json"),
        "Análise DFC": ("historico_analise_dfc", "resultado_json"),
        "Análise Patrimonial (DVP)": ("historico_analise_patrimonial", "resultado_json"),
        "Análise Orçamentária (BO)": ("historico_analise_orcamentaria", "resultado_json"),
        "Análise Financeira (BF)": ("historico_analise_financeira_bf", "resultado_json"),
        "Comparativo de Receitas": ("historico_comparativo_receitas", "dados_json"),
        "Comparativo de Despesas": ("historico_comparativo_despesas", "dados_json"),
        "Panorama de Resultados": ("historico_panorama", "resultado_json"),
        "Índices de Liquidez": ("historico_liquidez", "resultado_json"),
        "Integridade entre Demonstrações": ("historico_integridade_matriz", "resultado_json"),
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
        
        # Monta o HTML dos módulos
        html_modulos = ""
        for i, m in enumerate(modulos_lista):
            nome = m.get("nome", "Módulo")
            data_mod = m.get("data_geracao", "N/A")
            
            html_modulos += f'<div class="page-break"></div>'
            html_modulos += f'<h2>{i+1}. {nome}</h2>'
            html_modulos += f'<p style="color:#666; font-style:italic;">Gerado em: {data_mod}</p>'
            
            tabela, coluna = mapa_tabelas.get(nome, (None, None))
            if not tabela:
                html_modulos += '<p style="color:red;">Módulo sem mapeamento.</p>'
                continue
            
            try:
                cursor.execute(f"SELECT {coluna} FROM {tabela} WHERE periodo LIKE %s ORDER BY id DESC LIMIT 1", (f"%{periodo}%",))
                mod_row = cursor.fetchone()
                
                if not mod_row or not mod_row[0]:
                    html_modulos += '<p style="color:red;">Dados não encontrados para este período.</p>'
                    continue
                
                mod_dados = json.loads(mod_row[0])
                
                # --- Renderização por módulo ---
                if nome == "Análise BP":
                    dados_bp = mod_dados.get("dados", {})
                    html_modulos += '<table><thead><tr><th>CONTA</th><th>PERÍODO ATUAL</th><th>PERÍODO ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>'
                    for k, v in dados_bp.items():
                        if isinstance(v, dict):
                            atual = v.get("atual", 0)
                            anterior = v.get("anterior", 0)
                            var = ((atual - anterior) / anterior * 100) if anterior else 0
                            html_modulos += f'<tr><td>{k.replace("_", " ").title()}</td><td class="text-right">{fmt(atual)}</td><td class="text-right">{fmt(anterior)}</td><td class="text-right">{pct(var)}</td></tr>'
                    html_modulos += '</tbody></table>'
                    
                    html_modulos += '<div class="alerta-info"><strong>Evolução das Principais Contas (R$)</strong><br>'
                    html_modulos += '1. Ativo Circulante, variação positiva de 40,66%.<br>'
                    html_modulos += '2. Variação do caixa, negativa de 11,93%.<br>'
                    html_modulos += '2.3 Ativo Realizável, variação positiva de 18.405.326,01%.<br>'
                    html_modulos += '4. Passivo Não Circulante, variação negativa de 95,74%.<br>'
                    html_modulos += '5. Patrimônio Líquido, variação positiva de 90,80%.<br>'
                    html_modulos += '6. Superávit Financeiro, variação negativa de 44,19%.</div>'
                
                elif nome == "Comparativo de Receitas":
                    atual = mod_dados.get("atual", {})
                    html_modulos += '<h3>Resumo</h3><table><thead><tr><th>INDICADOR</th><th>VALOR</th></tr></thead><tbody>'
                    html_modulos += f'<tr><td>Receita Orçada</td><td class="text-right">{fmt(atual.get("orcado_total"))}</td></tr>'
                    html_modulos += f'<tr><td>Receita Realizada</td><td class="text-right">{fmt(atual.get("realizado_total"))}</td></tr>'
                    html_modulos += f'<tr><td>% Execução</td><td class="text-right">{atual.get("percentual_total", 0)}%</td></tr>'
                    html_modulos += '</tbody></table>'
                    
                    html_modulos += '<h3>Composição por Grupo</h3><table><thead><tr><th>GRUPO</th><th>ORÇADO</th><th>REALIZADO</th><th>%</th></tr></thead><tbody>'
                    for g in atual.get("grupos", []):
                        html_modulos += f'<tr><td>{g.get("nome","")}</td><td class="text-right">{fmt(g.get("orcado"))}</td><td class="text-right">{fmt(g.get("realizado"))}</td><td class="text-right">{g.get("percentual",0):.2f}%</td></tr>'
                    html_modulos += '</tbody></table>'
                
                elif nome == "Comparativo de Despesas":
                    atual = mod_dados.get("atual", {})
                    html_modulos += '<h3>Resumo</h3><table><thead><tr><th>INDICADOR</th><th>VALOR</th></tr></thead><tbody>'
                    html_modulos += f'<tr><td>Despesa Orçada</td><td class="text-right">{fmt(atual.get("orcado_total"))}</td></tr>'
                    html_modulos += f'<tr><td>Despesa Empenhada</td><td class="text-right">{fmt(atual.get("empenhado_total"))}</td></tr>'
                    html_modulos += f'<tr><td>Despesa Liquidada</td><td class="text-right">{fmt(atual.get("liquidado_total"))}</td></tr>'
                    html_modulos += f'<tr><td>% Execução</td><td class="text-right">{atual.get("percentual_total", 0)}%</td></tr>'
                    html_modulos += '</tbody></table>'
                    
                    html_modulos += '<h3>Composição por Grupo</h3><table><thead><tr><th>GRUPO</th><th>ORÇADO</th><th>EMPENHADO</th><th>LIQUIDADO</th><th>%</th></tr></thead><tbody>'
                    for g in atual.get("grupos", []):
                        html_modulos += f'<tr><td>{g.get("nome","")}</td><td class="text-right">{fmt(g.get("orcado"))}</td><td class="text-right">{fmt(g.get("empenhado"))}</td><td class="text-right">{fmt(g.get("liquidado"))}</td><td class="text-right">{g.get("percentual",0):.2f}%</td></tr>'
                    html_modulos += '</tbody></table>'
                
                elif nome == "Integridade entre Demonstrações":
                    matriz = mod_dados.get("matriz", [])
                    html_modulos += '<table><thead><tr><th>ITEM</th><th>BALANCETE</th><th>BP</th><th>BF</th><th>BO</th><th>DFC</th><th>DVP</th><th>DMPL</th><th>CONF</th></tr></thead><tbody>'
                    for mi in matriz:
                        html_modulos += f'<tr><td>{mi.get("item","")}</td><td class="text-right">{mi.get("balancete","")}</td><td class="text-right">{mi.get("bp","")}</td><td class="text-right">{mi.get("bf","")}</td><td class="text-right">{mi.get("bo","")}</td><td class="text-right">{mi.get("dfc","")}</td><td class="text-right">{mi.get("dvp","")}</td><td class="text-right">{mi.get("dmpl","")}</td><td class="text-center">{mi.get("conf","")}</td></tr>'
                    html_modulos += '</tbody></table>'
                    
                    html_modulos += '<div class="alerta-info">1. Os itens de conformidade em vermelho, de 1 a 4, são por estornos de restos a pagar.<br>2. Incorporação de Ativos: 1.2.3.1.1.01.99 • Outras Máq, Apar, Equip - R$ 65.962,97; 1.2.3.1.1.03.03 - Mobiliário - R$ 240.628,83; 1.2.3.2.1.99.01 - Edifício - R$ 6.682.639,01; 3.3.1.1.48 - Bens Não Ativáveis - R$ 21.081,55; PLATEC - R$ 9.261.645,32. SOMA = 16.271.957,08.</div>'
                
                elif nome == "Índices de Liquidez":
                    liq = mod_dados.get("liquidez", {})
                    est = mod_dados.get("estrutura", {})
                    html_modulos += '<h3>Liquidez</h3><table><thead><tr><th>INDICADOR</th><th>ATUAL</th></tr></thead><tbody>'
                    for k, v in liq.items():
                        html_modulos += f'<tr><td>{k.replace("_", " ").title()}</td><td class="text-right">{v}</td></tr>'
                    html_modulos += '</tbody></table>'
                    html_modulos += '<h3>Estrutura Patrimonial</h3><table><thead><tr><th>INDICADOR</th><th>ATUAL</th></tr></thead><tbody>'
                    for k, v in est.items():
                        html_modulos += f'<tr><td>{k.replace("_", " ").title()}</td><td class="text-right">{v}</td></tr>'
                    html_modulos += '</tbody></table>'
                
                elif nome == "Panorama de Resultados":
                    html_modulos += '<table><thead><tr><th>INDICADOR</th><th>VALOR</th></tr></thead><tbody>'
                    for k, v in mod_dados.items():
                        if isinstance(v, (int, float)):
                            html_modulos += f'<tr><td>{k.replace("_", " ").title()}</td><td class="text-right">{fmt(v)}</td></tr>'
                    html_modulos += '</tbody></table>'
                
                elif nome == "Custo de Pessoal":
                    html_modulos += '<table><thead><tr><th>INDICADOR</th><th>VALOR</th></tr></thead><tbody>'
                    html_modulos += f'<tr><td>RCL Total</td><td class="text-right">{fmt(mod_dados.get("rcl_total"))}</td></tr>'
                    html_modulos += f'<tr><td>Custo Total</td><td class="text-right">{fmt(mod_dados.get("custo_atual"))}</td></tr>'
                    html_modulos += f'<tr><td>Limite Legal (50%)</td><td class="text-right">{fmt(mod_dados.get("limite_total"))}</td></tr>'
                    html_modulos += f'<tr><td>Margem Disponível</td><td class="text-right">{fmt(mod_dados.get("margem_disponivel_total"))}</td></tr>'
                    html_modulos += f'<tr><td>% Custo sobre RCL</td><td class="text-right">{mod_dados.get("pct_custo", 0)}%</td></tr>'
                    html_modulos += '</tbody></table>'
                
                elif nome == "Análise por Centro de Custos":
                    centros = mod_dados.get("centros", [])
                    html_modulos += '<table><thead><tr><th>CENTRO DE CUSTO</th><th>VALOR</th></tr></thead><tbody>'
                    for c in centros:
                        html_modulos += f'<tr><td>{c.get("nome","")}</td><td class="text-right">{fmt(c.get("valor"))}</td></tr>'
                    html_modulos += '</tbody></table>'
                
                elif nome == "Análise DFC":
                    dados_dfc = mod_dados.get("dados", {})
                    for tipo in ["operacional", "investimento", "financiamento"]:
                        if tipo in dados_dfc:
                            html_modulos += f'<h3>Fluxo {tipo.title()}</h3><table><thead><tr><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th></tr></thead><tbody>'
                            for k, v in dados_dfc[tipo].items():
                                if isinstance(v, dict):
                                    html_modulos += f'<tr><td>{k.title()}</td><td class="text-right">{fmt(v.get("atual"))}</td><td class="text-right">{fmt(v.get("anterior"))}</td></tr>'
                            html_modulos += '</tbody></table>'
                
                elif nome == "Análise Patrimonial (DVP)":
                    html_modulos += '<table><thead><tr><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th></tr></thead><tbody>'
                    for k, v in mod_dados.items():
                        if isinstance(v, dict):
                            html_modulos += f'<tr><td>{k.replace("_", " ").title()}</td><td class="text-right">{fmt(v.get("atual"))}</td><td class="text-right">{fmt(v.get("anterior"))}</td></tr>'
                    html_modulos += '</tbody></table>'
                
                elif nome == "Análise Orçamentária (BO)":
                    atual = mod_dados.get("atual", {})
                    html_modulos += '<table><thead><tr><th>INDICADOR</th><th>ATUAL</th></tr></thead><tbody>'
                    html_modulos += f'<tr><td>Receita Realizada</td><td class="text-right">{fmt(atual.get("receita_realizada"))}</td></tr>'
                    html_modulos += f'<tr><td>Despesa Empenhada</td><td class="text-right">{fmt(atual.get("despesa_empenhada"))}</td></tr>'
                    html_modulos += f'<tr><td>Superávit/Déficit</td><td class="text-right">{fmt(atual.get("superavit"))}</td></tr>'
                    html_modulos += '</tbody></table>'
                
                elif nome == "Análise Financeira (BF)":
                    atual = mod_dados.get("atual", {})
                    html_modulos += '<table><thead><tr><th>INDICADOR</th><th>ATUAL</th><th>ANTERIOR</th></tr></thead><tbody>'
                    for k, v in atual.items():
                        if isinstance(v, dict):
                            html_modulos += f'<tr><td>{k.replace("_", " ").title()}</td><td class="text-right">{fmt(v.get("atual"))}</td><td class="text-right">{fmt(v.get("anterior"))}</td></tr>'
                    html_modulos += '</tbody></table>'
                
                elif nome == "Conferência das Demonstrações":
                    analises = mod_dados.get("analises", [])
                    for a in analises:
                        html_modulos += f'<h3>{a.get("titulo", "")}</h3>'
                        html_modulos += f'<p>{a.get("conceito", "")}</p>'
                        html_modulos += '<table><thead><tr><th>ITEM</th><th>VALOR</th></tr></thead><tbody>'
                        for t in a.get("tabela", []):
                            html_modulos += f'<tr><td>{t.get("label","")}</td><td class="text-right">{t.get("valor","")}</td></tr>'
                        html_modulos += '</tbody></table>'
                        html_modulos += f'<p><strong>Status:</strong> {a.get("status","")} - {a.get("mensagem","")}</p>'
                
                else:
                    html_modulos += f'<pre>{json.dumps(mod_dados, ensure_ascii=False, indent=2)[:2000]}</pre>'
                    
            except Exception as e:
                html_modulos += f'<p style="color:red;">Erro ao processar módulo: {str(e)}</p>'
        
        cursor.close()
        conn.close()
        
        # Carrega o template e substitui as variáveis
        template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template_relatorio.html")
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
        
        html_final = template.replace("{periodo}", periodo).replace("{modulos}", html_modulos)
        
        # Gera o PDF com WeasyPrint
        pdf_bytes = HTML(string=html_final).write_pdf()
        return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=relatorio_{periodo}.pdf"})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(content=f"Erro ao gerar PDF: {str(e)}", status_code=500, media_type="text/plain")'''

    conteudo = conteudo[:idx_inicio] + nova_funcao + conteudo[idx_fim:]
    print("✅ Função 'gerar_pdf_relatorio_consolidado' reescrita com WeasyPrint (HTML/CSS).")
else:
    print("❌ Função não encontrada.")

# Verifica sintaxe e salva
try:
    ast.parse(conteudo)
    with open(caminho_main, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
