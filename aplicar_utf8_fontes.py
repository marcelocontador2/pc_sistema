import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_utf8_fontes_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

def aplicar_fonte(bloco):
    # Verifica se a fonte Arial ja foi registrada
    if 'pdf.add_font("Arial"' not in bloco:
        idx = bloco.find("pdf = FPDF(")
        if idx != -1:
            fim_linha = bloco.find("\n", idx) + 1
            # Adiciona o bloco de registro da fonte
            linhas = """
    # --- REGISTRO DA FONTE UTF-8 (Arial) ---
    import os
    pasta_fontes = os.path.dirname(os.path.abspath(__file__))
    try:
        pdf.add_font("Arial", "", os.path.join(pasta_fontes, "arial.ttf"))
        pdf.add_font("Arial", "B", os.path.join(pasta_fontes, "arialbd.ttf"))
        pdf.add_font("Arial", "I", os.path.join(pasta_fontes, "ariali.ttf"))
        fonte_padrao = "Arial"
    except Exception:
        fonte_padrao = "Helvetica"
"""
            bloco = bloco[:fim_linha] + linhas + bloco[fim_linha:]
    
    # Substitui 'Helvetica' por 'fonte_padrao' nos set_font
    bloco = bloco.replace('pdf.set_font("Helvetica"', 'pdf.set_font(fonte_padrao')
    return bloco

rotas = [
    '@app.get("/gerar_pdf_relatorio_consolidado/{id}")',
    '@app.get("/gerar_pdf_analise_financeira_bf/{id}")',
    '@app.get("/gerar_pdf_analise_dfc/{id}")'
]

for rota in rotas:
    idx = c.find(rota)
    if idx == -1:
        print(f"[AVISO] Rota {rota} nao encontrada.")
        continue
    
    fim = c.find('@app', idx + 10)
    if fim == -1:
        fim = len(c)
    
    bloco_antigo = c[idx:fim]
    bloco_novo = aplicar_fonte(bloco_antigo)
    
    if bloco_novo != bloco_antigo:
        c = c[:idx] + bloco_novo + c[fim:]
        print(f"[OK] Fonte UTF-8 (Arial) aplicada em: {rota}")
    else:
        print(f"[AVISO] Nenhuma alteracao necessaria em: {rota}")

open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Sintaxe validada. Alteracoes salvas.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_utf8_fontes_{ts}", back_path)
    print("[OK] Backup restaurado.")
