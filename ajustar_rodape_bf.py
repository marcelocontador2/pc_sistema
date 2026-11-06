import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_ajuste_rodape_bf_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# 1. Reduzir o espacamento entre as tabelas (y_pos += 10 para += 5)
c = c.replace("        y_pos += 10\n        \n        # Calculos de Ingressos", "        y_pos += 5\n        \n        # Calculos de Ingressos")
c = c.replace("        # Calculos de Dispêndios\n        y_pos += 10", "        # Calculos de Dispêndios\n        y_pos += 5")

# 2. Reduzir a altura das linhas da tabela (de 7 para 6)
c = c.replace("pdf.cell(90, 7, nome, border=1, fill=bool(fill_color))", "pdf.cell(90, 6, nome, border=1, fill=bool(fill_color))")
c = c.replace("pdf.cell(40, 7, fmt(at), border=1, align=\"R\", fill=bool(fill_color))", "pdf.cell(40, 6, fmt(at), border=1, align=\"R\", fill=bool(fill_color))")
c = c.replace("pdf.cell(40, 7, fmt(ant), border=1, align=\"R\", fill=bool(fill_color))", "pdf.cell(40, 6, fmt(ant), border=1, align=\"R\", fill=bool(fill_color))")
c = c.replace("y_pos += 7", "y_pos += 6")

# 3. Reduzir a altura dos cabecalhos de grupo (de 7 para 6)
c = c.replace("pdf.cell(170, 7, \"RECEITAS\", border=1, fill=True)", "pdf.cell(170, 6, \"RECEITAS\", border=1, fill=True)")
c = c.replace("pdf.cell(170, 7, \"DESPESAS\", border=1, fill=True)", "pdf.cell(170, 6, \"DESPESAS\", border=1, fill=True)")
c = c.replace("pdf.cell(170, 7, \"EXTRAORCAMENTARIO\", border=1, fill=True)", "pdf.cell(170, 6, \"EXTRAORCAMENTARIO\", border=1, fill=True)")
c = c.replace("pdf.cell(170, 7, \"CAIXA E EQUIVALENTES\", border=1, fill=True)", "pdf.cell(170, 6, \"CAIXA E EQUIVALENTES\", border=1, fill=True)")
c = c.replace("pdf.cell(170, 7, \"TOTAL GERAL DE INGRESSOS\", border=1, fill=True)", "pdf.cell(170, 6, \"TOTAL GERAL DE INGRESSOS\", border=1, fill=True)")
c = c.replace("pdf.cell(170, 7, \"TOTAL GERAL DE DISPENDIOS\", border=1, fill=True)", "pdf.cell(170, 6, \"TOTAL GERAL DE DISPENDIOS\", border=1, fill=True)")

# 4. Mover o rodape para Y=275 (um pouco mais para cima) ou so desenhar se y_pos < 270
# Vamos trocar o desenho do rodape fixo por uma verificacao
antigo_rodape = """        # Rodape
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.3)
        pdf.line(15, 285, 195, 285)
        pdf.set_text_color(120, 120, 120)
        pdf.set_font(fonte_padrao, "I", 8)
        pdf.set_xy(15, 287)
        pdf.cell(90, 5, "Cofen - Analise das Demonstracoes Contabeis", new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_xy(135, 287)
        pdf.cell(60, 5, f"Gerado em: {datetime.now():%d/%m/%Y %H:%M}", align="R")"""

novo_rodape = """        # Rodape - Posiciona dinamicamente, abaixo da ultima linha (se houver espaco)
        y_rodape = max(y_pos + 5, 270)
        if y_rodape > 280:
            y_rodape = 280
        
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.3)
        pdf.line(15, y_rodape, 195, y_rodape)
        pdf.set_text_color(120, 120, 120)
        pdf.set_font(fonte_padrao, "I", 8)
        pdf.set_xy(15, y_rodape + 2)
        pdf.cell(90, 5, "Cofen - Analise das Demonstracoes Contabeis", new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_xy(135, y_rodape + 2)
        pdf.cell(60, 5, f"Gerado em: {datetime.now():%d/%m/%Y %H:%M}", align="R")"""

if antigo_rodape in c:
    c = c.replace(antigo_rodape, novo_rodape, 1)
    print("[OK] Rodape ajustado dinamicamente.")
else:
    print("[AVISO] Trecho do rodape nao encontrado. Tentando variacao...")
    # Tenta so mover o Y de 285 para 275
    c = c.replace("pdf.line(15, 285, 195, 285)", "pdf.line(15, 275, 195, 275)")
    c = c.replace("pdf.set_xy(15, 287)", "pdf.set_xy(15, 277)")
    c = c.replace("pdf.set_xy(135, 287)", "pdf.set_xy(135, 277)")
    print("[OK] Rodape movido para Y=275 (fallback).")

open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_ajuste_rodape_bf_{ts}", back_path)
    print("[OK] Backup restaurado.")
