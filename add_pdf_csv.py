import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_pdf_csv_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Verifica se a rota já existe
if '@app.get("/download/pdf_csv/{tipo}")' not in c:
    nova_rota = '''
@app.get("/download/pdf_csv/{tipo}")
async def download_pdf_csv(tipo: str, ano: int = Query(2026), periodo: str = Query("")):
    from fpdf import FPDF
    from fastapi.responses import Response
    import os
    
    # Mapeia o tipo para o nome do arquivo
    mapa = {
        "COMPARATIVO_DESPESAS": "COMPARATIVO_DESPESAS",
        "COMPARATIVO_RECEITAS": "COMPARATIVO_RECEITAS",
        "CENTRO_CUSTOS": "CENTRO_CUSTOS"
    }
    
    prefixo = mapa.get(tipo.upper(), tipo.upper())
    # Procura o arquivo mais recente com esse prefixo
    pasta = r"C:\\Users\\Marcelo Medeiros\\pc_sistema\\pc_storage\\uploads_raw"
    arquivo = None
    for f in sorted(os.listdir(pasta), reverse=True):
        if f.startswith(prefixo) and f.endswith(".csv"):
            arquivo = os.path.join(pasta, f)
            break
    
    if not arquivo:
        return {"erro": True, "mensagem": f"Arquivo CSV para {tipo} não encontrado."}
    
    # Lê o CSV
    try:
        with open(arquivo, "r", encoding="utf-8-sig") as f:
            linhas = f.readlines()
    except:
        with open(arquivo, "r", encoding="latin-1") as f:
            linhas = f.readlines()
    
    # Gera o PDF
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    
    # Título
    pdf.set_font("Helvetica", "B", 16)
    titulo = tipo.replace("_", " ").title()
    pdf.cell(0, 10, f"Relatório - {titulo}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Arquivo: {os.path.basename(arquivo)}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    
    # Cabeçalho da tabela
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(0, 114, 186)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(80, 8, "Descrição", border=1, fill=True, align="C")
    pdf.cell(30, 8, "Orçado", border=1, fill=True, align="C")
    pdf.cell(30, 8, "Realizado", border=1, fill=True, align="C")
    pdf.cell(30, 8, "%", border=1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    
    # Dados (pula linhas de cabeçalho)
    count = 0
    for linha in linhas:
        if ";" not in linha: continue
        partes = linha.strip().split(";")
        if len(partes) < 3: continue
        nome = partes[0].strip().strip('"')[:50]
        if not nome or "COFEN" in nome.upper() or "PERIODO" in nome.upper(): continue
        orcado = partes[1].strip() if len(partes) > 1 else ""
        realizado = partes[2].strip() if len(partes) > 2 else ""
        pct = partes[3].strip() if len(partes) > 3 else ""
        if not orcado or orcado == "Orçado": continue
        
        pdf.set_font("Helvetica", "", 7)
        pdf.cell(80, 6, nome, border=1)
        pdf.cell(30, 6, orcado, border=1, align="R")
        pdf.cell(30, 6, realizado, border=1, align="R")
        pdf.cell(30, 6, pct, border=1, align="R", new_x="LMARGIN", new_y="NEXT")
        count += 1
        if count > 60: break
    
    out = pdf.output()
    return Response(content=bytes(out), media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="relatorio_{tipo}_{ano}.pdf"'})
'''
    c += nova_rota
    open(back_path, 'w', encoding='utf-8').write(c)
    print("[OK] Rota /download/pdf_csv/{tipo} adicionada ao backend.")
else:
    print("[AVISO] Rota já existe.")

# Valida
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_pdf_csv_{ts}", back_path)
    print("[OK] Backup restaurado")
