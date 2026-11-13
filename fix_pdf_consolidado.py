import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_pdf_consolidado")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza a função gerar_pdf_relatorio_consolidado
idx_inicio = conteudo.find("def gerar_pdf_relatorio_consolidado(")
if idx_inicio != -1:
    # Encontra o final da função (próxima @app ou def)
    idx_fim = conteudo.find("\n@app.", idx_inicio)
    if idx_fim == -1:
        idx_fim = len(conteudo)
    
    nova_funcao = '''def gerar_pdf_relatorio_consolidado(id: int):
    from fastapi.responses import Response
    import json
    import psycopg2
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    import io
    
    PG_CONFIG = {
        "host": "localhost", "port": 5433,
        "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
    }
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_relatorio_consolidado WHERE id = %s", (id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            return Response(content="Relatório não encontrado.", status_code=404, media_type="text/plain")
        
        periodo, data_geracao, res_json = row
        dados = json.loads(res_json)
        modulos = dados.get("dados", [])
        
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        
        # Título
        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, "RELATÓRIO CONSOLIDADO DE ANÁLISE CONTÁBIL", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        
        pdf.set_font("helvetica", "I", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Período: {periodo} | Gerado em: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(10)
        
        # Lista os módulos encontrados
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(51, 51, 51)
        pdf.cell(0, 10, "Módulos Consolidados:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        pdf.set_font("helvetica", "", 10)
        for i, m in enumerate(modulos):
            nome = m.get("nome", "Módulo desconhecido")
            data = m.get("data_geracao", "N/A")
            pdf.cell(0, 8, f"{i+1}. {nome} - {data}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Gera o PDF em memória e retorna
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=relatorio_{periodo}.pdf"})
        
    except Exception as e:
        return Response(content=f"Erro ao gerar PDF: {str(e)}", status_code=500, media_type="text/plain")'''
    
    conteudo = conteudo[:idx_inicio] + nova_funcao + conteudo[idx_fim:]
    print("✅ Função 'gerar_pdf_relatorio_consolidado' atualizada para buscar dados reais.")
else:
    print("❌ Função de gerar PDF não encontrada.")

# Verifica sintaxe e salva
try:
    ast.parse(conteudo)
    with open(caminho_main, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
