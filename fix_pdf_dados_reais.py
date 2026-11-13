import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_pdf_completo_real")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza a função gerar_pdf_relatorio_consolidado
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
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    from datetime import datetime
    
    PG_CONFIG = {
        "host": "localhost", "port": 5433,
        "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
    }
    
    def fmt(v):
        if v is None: return "-"
        if isinstance(v, (int, float)):
            return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return str(v)
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_relatorio_consolidado WHERE id = %s", (id,))
        row = cursor.fetchone()
        if not row:
            return Response(content="Relatório não encontrado.", status_code=404, media_type="text/plain")
        
        periodo, data_geracao, res_json = row
        dados = json.loads(res_json)
        modulos_lista = dados.get("dados", [])
        
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # --- CAPA ---
        pdf.add_page()
        pdf.set_font("helvetica", "B", 20)
        pdf.set_text_color(0, 51, 102)
        pdf.ln(60)
        pdf.cell(0, 15, "RELATÓRIO CONSOLIDADO", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, "DE ANÁLISE CONTÁBIL", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(20)
        pdf.set_font("helvetica", "I", 11)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 8, f"Período: {periodo}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.cell(0, 8, f"Gerado em: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        
        # --- MÓDULOS ---
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
        
        for i, m in enumerate(modulos_lista):
            nome = m.get("nome", "Módulo")
            data_mod = m.get("data_geracao", "N/A")
            
            pdf.add_page()
            pdf.set_font("helvetica", "B", 14)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(0, 10, f"{i+1}. {nome}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("helvetica", "I", 9)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 5, f"Gerado em: {data_mod}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)
            
            tabela, coluna = mapa_tabelas.get(nome, (None, None))
            if not tabela:
                pdf.set_font("helvetica", "I", 10)
                pdf.set_text_color(200, 0, 0)
                pdf.cell(0, 5, "Módulo sem mapeamento de tabela.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                continue
            
            try:
                cursor.execute(f"SELECT {coluna} FROM {tabela} WHERE periodo = %s ORDER BY id DESC LIMIT 1", (periodo,))
                mod_row = cursor.fetchone()
                if not mod_row or not mod_row[0]:
                    pdf.set_font("helvetica", "I", 10)
                    pdf.set_text_color(200, 0, 0)
                    pdf.cell(0, 5, "Dados não encontrados no banco para este período.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    continue
                
                mod_dados = json.loads(mod_row[0])
                pdf.set_font("helvetica", "", 9)
                pdf.set_text_color(30, 30, 30)
                
                # Renderização específica por módulo
                if nome == "Análise BP":
                    dados_bp = mod_dados.get("dados", {})
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(0, 6, "Conta | Atual | Anterior", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_font("helvetica", "", 9)
                    for k, v in dados_bp.items():
                        if isinstance(v, dict):
                            atual = fmt(v.get("atual"))
                            anterior = fmt(v.get("anterior"))
                            pdf.cell(0, 5, f"{k.replace('_', ' ').title()}: {atual} | {anterior}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                elif nome == "Análise Financeira (BF)":
                    atual = mod_dados.get("atual", {})
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(0, 6, "Indicador | Atual | Anterior", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_font("helvetica", "", 9)
                    for k, v in atual.items():
                        if isinstance(v, dict):
                            a = fmt(v.get("atual"))
                            ant = fmt(v.get("anterior"))
                            pdf.cell(0, 5, f"{k.replace('_', ' ').title()}: {a} | {ant}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                elif nome == "Análise Orçamentária (BO)":
                    atual = mod_dados.get("atual", {})
                    pdf.set_font("helvetica", "", 9)
                    pdf.cell(0, 5, f"Receita Realizada: {fmt(atual.get('receita_realizada'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 5, f"Despesa Empenhada: {fmt(atual.get('despesa_empenhada'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 5, f"Superávit/Déficit: {fmt(atual.get('superavit'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                elif nome == "Comparativo de Receitas":
                    atual = mod_dados.get("atual", {})
                    pdf.cell(0, 5, f"Orçado Total: {fmt(atual.get('orcado_total'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 5, f"Realizado Total: {fmt(atual.get('realizado_total'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 5, f"Percentual: {atual.get('percentual_total', 0)}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                elif nome == "Comparativo de Despesas":
                    atual = mod_dados.get("atual", {})
                    pdf.cell(0, 5, f"Orçado Total: {fmt(atual.get('orcado_total'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 5, f"Empenhado Total: {fmt(atual.get('empenhado_total'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 5, f"Percentual: {atual.get('percentual_total', 0)}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                elif nome == "Panorama de Resultados":
                    for k, v in mod_dados.items():
                        if isinstance(v, (int, float)):
                            pdf.cell(0, 5, f"{k.replace('_', ' ').title()}: {fmt(v)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                elif nome == "Índices de Liquidez":
                    liquidez = mod_dados.get("liquidez", {})
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(0, 6, "Liquidez:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_font("helvetica", "", 9)
                    for k, v in liquidez.items():
                        pdf.cell(0, 5, f"{k.replace('_', ' ').title()}: {v}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                elif nome == "Integridade entre Demonstrações":
                    matriz = mod_dados.get("matriz", [])
                    pdf.set_font("helvetica", "B", 9)
                    pdf.cell(0, 6, "Item | Balancete | BP | BF | BO | DFC | DVP | DMPL | Conf.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_font("helvetica", "", 8)
                    for m_item in matriz:
                        linha = f"{m_item.get('item','')[:25]} | {m_item.get('balancete','')} | {m_item.get('bp','')} | {m_item.get('bf','')} | {m_item.get('bo','')} | {m_item.get('dfc','')} | {m_item.get('dvp','')} | {m_item.get('dmpl','')} | {m_item.get('conf','')}"
                        pdf.cell(0, 5, linha, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                elif nome == "Conferência das Demonstrações":
                    analises = mod_dados.get("analises", [])
                    pdf.set_font("helvetica", "", 9)
                    for a in analises:
                        pdf.set_font("helvetica", "B", 10)
                        pdf.cell(0, 6, a.get("titulo", ""), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.set_font("helvetica", "", 9)
                        pdf.multi_cell(0, 4, a.get("conceito", ""))
                        for t in a.get("tabela", []):
                            pdf.cell(0, 4, f"  {t.get('label','')}: {t.get('valor','')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.cell(0, 5, f"  Status: {a.get('status','')} - {a.get('mensagem','')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.ln(3)
                
                elif nome == "Custo de Pessoal":
                    pdf.cell(0, 5, f"RCL Atual: {fmt(mod_dados.get('rcl_atual'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 5, f"Custo Atual: {fmt(mod_dados.get('custo_atual'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 5, f"Limite Total: {fmt(mod_dados.get('limite_total'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 5, f"Margem Disponível: {fmt(mod_dados.get('margem_disponivel_total'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                elif nome == "Análise por Centro de Custos":
                    centros = mod_dados.get("centros", [])
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(0, 6, "Centro de Custo | Valor", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_font("helvetica", "", 9)
                    for c in centros:
                        pdf.cell(0, 5, f"{c.get('nome','')[:60]}: {fmt(c.get('valor'))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                elif nome == "Análise DFC":
                    dados_dfc = mod_dados.get("dados", {})
                    for tipo in ["operacional", "investimento", "financiamento"]:
                        if tipo in dados_dfc:
                            pdf.set_font("helvetica", "B", 10)
                            pdf.cell(0, 6, f"Fluxo {tipo.title()}:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                            pdf.set_font("helvetica", "", 9)
                            for k, v in dados_dfc[tipo].items():
                                if isinstance(v, dict):
                                    a = fmt(v.get("atual"))
                                    ant = fmt(v.get("anterior"))
                                    pdf.cell(0, 5, f"  {k.title()}: {a} | {ant}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                elif nome == "Análise Patrimonial (DVP)":
                    for k, v in mod_dados.items():
                        if isinstance(v, dict):
                            a = fmt(v.get("atual"))
                            ant = fmt(v.get("anterior"))
                            pdf.cell(0, 5, f"{k.replace('_', ' ').title()}: {a} | {ant}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                else:
                    resumo = json.dumps(mod_dados, ensure_ascii=False, indent=2)[:2000]
                    pdf.multi_cell(0, 5, resumo)
                    
            except Exception as e:
                pdf.set_font("helvetica", "I", 9)
                pdf.set_text_color(200, 0, 0)
                pdf.cell(0, 5, f"Erro ao processar módulo: {str(e)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # --- PARECER DO CONTADOR ---
        pdf.add_page()
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, "PARECER DO CONTADOR", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(10)
        pdf.set_font("helvetica", "", 11)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 8, "Análise Concluída", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(20)
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
    print("✅ Função 'gerar_pdf_relatorio_consolidado' reescrita para renderizar os dados reais.")

# Verifica sintaxe e salva
try:
    ast.parse(conteudo)
    with open(caminho_main, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
