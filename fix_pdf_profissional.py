import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_pdf_profissional")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza a função
idx_inicio = conteudo.find("def gerar_pdf_relatorio_consolidado(")
if idx_inicio != -1:
    idx_fim = conteudo.find("\n@app.", idx_inicio)
    if idx_fim == -1:
        idx_fim = len(conteudo)
    
    nova_funcao = '''def gerar_pdf_relatorio_consolidado(id: int):
    from fastapi.responses import Response
    import json
    import psycopg2
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    
    PG_CONFIG = {
        "host": "localhost", "port": 5433,
        "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
    }
    
    # Funções auxiliares de formatação
    def fmt(v):
        if v is None: return "-"
        if isinstance(v, (int, float)):
            return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return str(v)
    
    def pct(v):
        if v is None: return "-"
        return f"{v:+.2f}%".replace(".", ",")
    
    # Mapa de tabelas (nome amigável -> tabela, coluna JSON)
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
        
        # Criar PDF
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # --- CAPA ---
        pdf.add_page()
        pdf.set_font("helvetica", "B", 22)
        pdf.set_text_color(0, 51, 102)
        pdf.ln(40)
        pdf.cell(0, 15, "RELATÓRIO CONSOLIDADO", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.set_font("helvetica", "B", 18)
        pdf.cell(0, 10, "DE ANÁLISE CONTÁBIL", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(15)
        pdf.set_font("helvetica", "", 12)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 8, "COFEN - Conselho Federal de Enfermagem", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(10)
        pdf.set_font("helvetica", "I", 11)
        pdf.cell(0, 8, f"Período: {periodo}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.cell(0, 8, f"Gerado em: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        
        # --- MÓDULOS (páginas internas) ---
        for i, m in enumerate(modulos_lista):
            nome = m.get("nome", "Módulo")
            data_mod = m.get("data_geracao", "N/A")
            
            pdf.add_page()
            
            # Cabeçalho do módulo
            pdf.set_font("helvetica", "B", 16)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(0, 10, f"{i+1}. {nome}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("helvetica", "I", 9)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 5, f"Gerado em: {data_mod}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)
            
            # Busca os dados do módulo no banco
            tabela, coluna = mapa_tabelas.get(nome, (None, None))
            if not tabela:
                pdf.set_font("helvetica", "", 10)
                pdf.set_text_color(200, 0, 0)
                pdf.cell(0, 5, "Módulo sem mapeamento de tabela.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                continue
            
            try:
                # Verifica se a tabela tem a coluna esperada
                cursor.execute(f"SELECT {coluna} FROM {tabela} WHERE periodo LIKE %s ORDER BY id DESC LIMIT 1", (f"%{periodo}%",))
                mod_row = cursor.fetchone()
                
                if not mod_row or not mod_row[0]:
                    pdf.set_font("helvetica", "", 10)
                    pdf.set_text_color(200, 0, 0)
                    pdf.cell(0, 5, "Dados não encontrados para este período.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    continue
                
                mod_dados = json.loads(mod_row[0])
                pdf.set_font("helvetica", "", 9)
                pdf.set_text_color(30, 30, 30)
                
                # Renderização específica por módulo
                if nome == "Análise BP":
                    dados_bp = mod_dados.get("dados", {})
                    pdf.set_font("helvetica", "B", 10)
                    pdf.set_fill_color(0, 51, 102)
                    pdf.set_text_color(255, 255, 255)
                    pdf.cell(70, 8, " CONTA", border=1, fill=True)
                    pdf.cell(40, 8, " ATUAL", border=1, fill=True, align="C")
                    pdf.cell(40, 8, " ANTERIOR", border=1, fill=True, align="C")
                    pdf.cell(30, 8, " VAR. %", border=1, fill=True, align="C")
                    pdf.ln()
                    pdf.set_font("helvetica", "", 9)
                    pdf.set_text_color(30, 30, 30)
                    for k, v in dados_bp.items():
                        if isinstance(v, dict):
                            atual = v.get("atual", 0)
                            anterior = v.get("anterior", 0)
                            var = ((atual - anterior) / anterior * 100) if anterior else 0
                            pdf.cell(70, 7, f" {k.replace('_', ' ').title()}", border=1)
                            pdf.cell(40, 7, f" {fmt(atual)}", border=1, align="R")
                            pdf.cell(40, 7, f" {fmt(anterior)}", border=1, align="R")
                            pdf.cell(30, 7, f" {pct(var)}", border=1, align="R")
                            pdf.ln()
                
                elif nome == "Comparativo de Receitas":
                    atual = mod_dados.get("atual", {})
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(0, 8, "Resumo", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_font("helvetica", "", 9)
                    pdf.cell(0, 6, f"Receita Orçada: {fmt(atual.get('orcado_total'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 6, f"Receita Realizada: {fmt(atual.get('realizado_total'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 6, f"% Execução: {atual.get('percentual_total', 0)}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    pdf.ln(5)
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(0, 8, "Composição por Grupo", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_font("helvetica", "", 8)
                    pdf.cell(80, 7, " GRUPO", border=1, fill=True)
                    pdf.cell(40, 7, " ORÇADO", border=1, fill=True, align="C")
                    pdf.cell(40, 7, " REALIZADO", border=1, fill=True, align="C")
                    pdf.cell(30, 7, " %", border=1, fill=True, align="C")
                    pdf.ln()
                    for g in atual.get("grupos", []):
                        pdf.cell(80, 6, f" {g.get('nome','')[:45]}", border=1)
                        pdf.cell(40, 6, f" {fmt(g.get('orcado'))}", border=1, align="R")
                        pdf.cell(40, 6, f" {fmt(g.get('realizado'))}", border=1, align="R")
                        pdf.cell(30, 6, f" {g.get('percentual',0):.2f}%", border=1, align="R")
                        pdf.ln()
                
                elif nome == "Comparativo de Despesas":
                    atual = mod_dados.get("atual", {})
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(0, 8, "Resumo", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_font("helvetica", "", 9)
                    pdf.cell(0, 6, f"Despesa Orçada: {fmt(atual.get('orcado_total'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 6, f"Despesa Empenhada: {fmt(atual.get('empenhado_total'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 6, f"Despesa Liquidada: {fmt(atual.get('liquidado_total'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 6, f"% Execução: {atual.get('percentual_total', 0)}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    pdf.ln(5)
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(0, 8, "Composição por Grupo", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_font("helvetica", "", 8)
                    pdf.cell(80, 7, " GRUPO", border=1, fill=True)
                    pdf.cell(30, 7, " ORÇADO", border=1, fill=True, align="C")
                    pdf.cell(30, 7, " EMPENHADO", border=1, fill=True, align="C")
                    pdf.cell(30, 7, " LIQUIDADO", border=1, fill=True, align="C")
                    pdf.cell(20, 7, " %", border=1, fill=True, align="C")
                    pdf.ln()
                    for g in atual.get("grupos", []):
                        pdf.cell(80, 6, f" {g.get('nome','')[:45]}", border=1)
                        pdf.cell(30, 6, f" {fmt(g.get('orcado'))}", border=1, align="R")
                        pdf.cell(30, 6, f" {fmt(g.get('empenhado'))}", border=1, align="R")
                        pdf.cell(30, 6, f" {fmt(g.get('liquidado'))}", border=1, align="R")
                        pdf.cell(20, 6, f" {g.get('percentual',0):.2f}%", border=1, align="R")
                        pdf.ln()
                
                elif nome == "Integridade entre Demonstrações":
                    matriz = mod_dados.get("matriz", [])
                    pdf.set_font("helvetica", "B", 7)
                    pdf.cell(45, 7, " ITEM", border=1, fill=True)
                    pdf.cell(18, 7, " BALANCETE", border=1, fill=True, align="C")
                    pdf.cell(18, 7, " BP", border=1, fill=True, align="C")
                    pdf.cell(18, 7, " BF", border=1, fill=True, align="C")
                    pdf.cell(18, 7, " BO", border=1, fill=True, align="C")
                    pdf.cell(18, 7, " DFC", border=1, fill=True, align="C")
                    pdf.cell(18, 7, " DVP", border=1, fill=True, align="C")
                    pdf.cell(18, 7, " DMPL", border=1, fill=True, align="C")
                    pdf.cell(15, 7, " CONF", border=1, fill=True, align="C")
                    pdf.ln()
                    pdf.set_font("helvetica", "", 7)
                    for mi in matriz:
                        pdf.cell(45, 6, f" {mi.get('item','')[:30]}", border=1)
                        pdf.cell(18, 6, f" {mi.get('balancete','')}", border=1, align="R")
                        pdf.cell(18, 6, f" {mi.get('bp','')}", border=1, align="R")
                        pdf.cell(18, 6, f" {mi.get('bf','')}", border=1, align="R")
                        pdf.cell(18, 6, f" {mi.get('bo','')}", border=1, align="R")
                        pdf.cell(18, 6, f" {mi.get('dfc','')}", border=1, align="R")
                        pdf.cell(18, 6, f" {mi.get('dvp','')}", border=1, align="R")
                        pdf.cell(18, 6, f" {mi.get('dmpl','')}", border=1, align="R")
                        pdf.cell(15, 6, f" {mi.get('conf','')}", border=1, align="C")
                        pdf.ln()
                
                elif nome == "Índices de Liquidez":
                    liq = mod_dados.get("liquidez", {})
                    est = mod_dados.get("estrutura", {})
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(0, 8, "Liquidez", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_font("helvetica", "", 9)
                    for k, v in liq.items():
                        pdf.cell(0, 6, f"{k.replace('_', ' ').title()}: {v}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.ln(3)
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(0, 8, "Estrutura Patrimonial", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_font("helvetica", "", 9)
                    for k, v in est.items():
                        pdf.cell(0, 6, f"{k.replace('_', ' ').title()}: {v}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                elif nome == "Panorama de Resultados":
                    for k, v in mod_dados.items():
                        if isinstance(v, (int, float)):
                            pdf.cell(0, 6, f"{k.replace('_', ' ').title()}: {fmt(v)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                elif nome == "Custo de Pessoal":
                    pdf.cell(0, 6, f"RCL Total: {fmt(mod_dados.get('rcl_total'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 6, f"Custo Total: {fmt(mod_dados.get('custo_atual'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 6, f"Limite Legal (50%): {fmt(mod_dados.get('limite_total'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 6, f"Margem Disponível: {fmt(mod_dados.get('margem_disponivel_total'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                elif nome == "Análise por Centro de Custos":
                    centros = mod_dados.get("centros", [])
                    pdf.set_font("helvetica", "B", 9)
                    pdf.cell(120, 7, " CENTRO DE CUSTO", border=1, fill=True)
                    pdf.cell(60, 7, " VALOR", border=1, fill=True, align="C")
                    pdf.ln()
                    pdf.set_font("helvetica", "", 8)
                    for c in centros:
                        pdf.cell(120, 6, f" {c.get('nome','')[:70]}", border=1)
                        pdf.cell(60, 6, f" {fmt(c.get('valor'))}", border=1, align="R")
                        pdf.ln()
                
                elif nome == "Análise DFC":
                    dados_dfc = mod_dados.get("dados", {})
                    for tipo in ["operacional", "investimento", "financiamento"]:
                        if tipo in dados_dfc:
                            pdf.set_font("helvetica", "B", 10)
                            pdf.cell(0, 8, f"Fluxo {tipo.title()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                            pdf.set_font("helvetica", "", 9)
                            for k, v in dados_dfc[tipo].items():
                                if isinstance(v, dict):
                                    a = fmt(v.get("atual"))
                                    ant = fmt(v.get("anterior"))
                                    pdf.cell(0, 6, f"  {k.title()}: {a} | {ant}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                elif nome == "Análise Patrimonial (DVP)":
                    for k, v in mod_dados.items():
                        if isinstance(v, dict):
                            a = fmt(v.get("atual"))
                            ant = fmt(v.get("anterior"))
                            pdf.cell(0, 6, f"{k.replace('_', ' ').title()}: {a} | {ant}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                elif nome == "Análise Orçamentária (BO)":
                    atual = mod_dados.get("atual", {})
                    pdf.cell(0, 6, f"Receita Realizada: {fmt(atual.get('receita_realizada'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 6, f"Despesa Empenhada: {fmt(atual.get('despesa_empenhada'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 6, f"Superávit/Déficit: {fmt(atual.get('superavit'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                elif nome == "Análise Financeira (BF)":
                    atual = mod_dados.get("atual", {})
                    for k, v in atual.items():
                        if isinstance(v, dict):
                            a = fmt(v.get("atual"))
                            ant = fmt(v.get("anterior"))
                            pdf.cell(0, 6, f"{k.replace('_', ' ').title()}: {a} | {ant}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                elif nome == "Conferência das Demonstrações":
                    analises = mod_dados.get("analises", [])
                    pdf.set_font("helvetica", "", 9)
                    for a in analises:
                        pdf.set_font("helvetica", "B", 10)
                        pdf.cell(0, 7, a.get("titulo", ""), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.set_font("helvetica", "", 8)
                        pdf.multi_cell(0, 4, a.get("conceito", ""))
                        for t in a.get("tabela", []):
                            pdf.cell(0, 4, f"  {t.get('label','')}: {t.get('valor','')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.cell(0, 5, f"  Status: {a.get('status','')} - {a.get('mensagem','')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.ln(2)
                
                else:
                    pdf.multi_cell(0, 5, json.dumps(mod_dados, ensure_ascii=False, indent=2)[:2000])
                
            except Exception as e:
                pdf.set_font("helvetica", "I", 9)
                pdf.set_text_color(200, 0, 0)
                pdf.cell(0, 5, f"Erro ao processar módulo: {str(e)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # --- PARECER DO CONTADOR ---
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, "PARECER DO CONTADOR", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(30, 30, 30)
        parecer_texto = """A entidade apresenta solidez financeira notável, evidenciada por um caixa elevado que suporta integralmente seus gastos operacionais. O índice de liquidez imediata de 15,93 e o índice de liquidez geral de 39,74 demonstram capacidade excepcional de honrar compromissos de curto e longo prazos. O endividamento geral de apenas 1,98% confirma uma estrutura de capital extremamente conservadora.

As receitas e despesas orçamentárias realizadas mantiveram-se no mesmo patamar do exercício anterior, indicando previsibilidade e controle na execução orçamentária.

A DFC revela geração líquida de caixa de R$ 17 milhões, correspondendo a um crescimento de 19,11% em relação ao período anterior.

O resultado patrimonial registrou acréscimo significativo de 421%. Contudo, trata-se de resultado contábil, sem reflexo financeiro imediato.

Custo de Pessoal: R$ 49 milhões, correspondendo a 29,76% do limite legal de 50%, com margem de 20,24% - situação confortável e em conformidade com os limites da Resolução Cofen 814/2026.

Verificou-se a integridade das demonstrações contábeis, que se apresentam adequadas e em conformidade com os princípios e normas aplicáveis.

O Cofen demonstra excelente saúde financeira e patrimonial, com liquidez amplamente favorável, endividamento irrisório, geração de caixa positiva e crescimento contábil expressivo. A execução orçamentária é estável e o custo com pessoal encontra-se dentro dos limites legais.

Recomenda-se: (i) manter o monitoramento dos centros de custo de maior expressão (AF 05); (ii) avaliar a aplicação do caixa elevado em instrumentos que preservem liquidez e rentabilidade; e (iii) acompanhar a natureza do resultado patrimonial para distinguir seus efeitos contábeis dos financeiros.

Conclusão: As demonstrações contábeis refletem equilíbrio, solidez e conformidade, não havendo indícios de risco financeiro ou descumprimento de limites legais."""
        
        pdf.multi_cell(0, 5, parecer_texto)
        pdf.ln(15)
        pdf.cell(0, 8, "_______________________________________", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 8, "Marcelo Ribeiro Medeiros", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 8, "CRC: 066005O8T/DF", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        cursor.close()
        conn.close()
        
        pdf_bytes = bytes(pdf.output(dest='S'))
        return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=relatorio_{periodo}.pdf"})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(content=f"Erro ao gerar PDF: {str(e)}", status_code=500, media_type="text/plain")'''

    conteudo = conteudo[:idx_inicio] + nova_funcao + conteudo[idx_fim:]
    print("✅ Função 'gerar_pdf_relatorio_consolidado' reescrita com layout profissional.")
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
