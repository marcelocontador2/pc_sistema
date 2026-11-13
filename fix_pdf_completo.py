import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_pdf_completo")

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
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        # 1. Busca o histórico consolidado (capa)
        cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_relatorio_consolidado WHERE id = %s", (id,))
        row = cursor.fetchone()
        
        if not row:
            return Response(content="Relatório não encontrado.", status_code=404, media_type="text/plain")
        
        periodo, data_geracao, res_json = row
        dados = json.loads(res_json)
        modulos = dados.get("dados", [])
        
        # 2. Mapeamento de módulos para tabelas do PostgreSQL
        mapa_tabelas = {
            "Análise BP": "historico_analise_bp",
            "Análise DFC": "historico_analise_dfc",
            "Análise Patrimonial (DVP)": "historico_analise_patrimonial",
            "Análise Orçamentária (BO)": "historico_analise_orcamentaria",
            "Análise Financeira (BF)": "historico_analise_financeira_bf",
            "Comparativo de Receitas": "historico_comparativo_receitas",
            "Comparativo de Despesas": "historico_comparativo_despesas",
            "Panorama de Resultados": "historico_panorama",
            "Índices de Liquidez": "historico_liquidez",
            "Integridade entre Demonstrações": "historico_integridade_matriz",
            "Conferência das Demonstrações": "historico_conferencia",
            "Custo de Pessoal": "historico_custo_pessoal",
            "Análise por Centro de Custos": "historico_centro_custos"
        }
        
        # 3. Cria o PDF
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        
        # --- CAPA ---
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 15, "RELATÓRIO CONSOLIDADO DE ANÁLISE CONTÁBIL", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        
        pdf.set_font("helvetica", "I", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Período: {periodo} | Gerado em: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(10)
        
        # --- MÓDULOS ---
        for i, m in enumerate(modulos):
            nome = m.get("nome", "Módulo desconhecido")
            data = m.get("data_geracao", "N/A")
            
            pdf.add_page()
            pdf.set_font("helvetica", "B", 14)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(0, 10, f"{i+1}. {nome}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            pdf.set_font("helvetica", "I", 9)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 5, f"Gerado em: {data}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)
            
            # Busca os dados do módulo no banco
            tabela = mapa_tabelas.get(nome)
            if tabela:
                try:
                    # Para a tabela de integridade, o campo é "resultado_json" (já foi tratado)
                    # Para as demais, o campo é "dados_json"
                    if tabela == "historico_integridade_matriz":
                        cursor.execute(f"SELECT resultado_json FROM {tabela} WHERE periodo = %s ORDER BY id DESC LIMIT 1", (periodo,))
                    else:
                        cursor.execute(f"SELECT dados_json FROM {tabela} WHERE periodo = %s ORDER BY id DESC LIMIT 1", (periodo,))
                    
                    modulo_row = cursor.fetchone()
                    if modulo_row:
                        modulo_dados = json.loads(modulo_row[0])
                        # Aqui renderizamos um resumo simples (primeiras chaves)
                        pdf.set_font("helvetica", "", 9)
                        pdf.set_text_color(51, 51, 51)
                        resumo = json.dumps(modulo_dados, ensure_ascii=False, indent=2)[:2000]
                        pdf.multi_cell(0, 5, resumo)
                    else:
                        pdf.set_font("helvetica", "I", 9)
                        pdf.set_text_color(200, 0, 0)
                        pdf.cell(0, 5, "Dados não encontrados no PostgreSQL para este período.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                except Exception as e:
                    pdf.set_font("helvetica", "I", 9)
                    pdf.set_text_color(200, 0, 0)
                    pdf.cell(0, 5, f"Erro ao buscar dados: {str(e)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            else:
                pdf.set_font("helvetica", "I", 9)
                pdf.set_text_color(200, 0, 0)
                pdf.cell(0, 5, "Módulo sem mapeamento de tabela.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        cursor.close()
        conn.close()
        
        # Gera o PDF em bytes (fpdf2 moderno já retorna bytearray)
        pdf_bytes = bytes(pdf.output(dest='S'))
        return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=relatorio_{periodo}.pdf"})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(content=f"Erro ao gerar PDF: {str(e)}", status_code=500, media_type="text/plain")'''

    conteudo = conteudo[:idx_inicio] + nova_funcao + conteudo[idx_fim:]
    print("✅ Função 'gerar_pdf_relatorio_consolidado' reescrita para incluir conteúdo real.")

# Verifica sintaxe e salva
try:
    ast.parse(conteudo)
    with open(caminho_main, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
