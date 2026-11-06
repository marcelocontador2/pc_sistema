import re, shutil, datetime, os

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_bf_dfc_utf8_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

# 1. Localiza uma fonte TTF para usar (Arial ou DejaVu)
# Vamos checar se existe alguma fonte no sistema ou na pasta do projeto
fontes_possiveis = [
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/Arial.ttf",
    "C:/Windows/Fonts/calibri.ttf",
    "C:/Windows/Fonts/Calibri.ttf",
    "C:/Windows/Fonts/DejaVuSans.ttf",
    os.path.join(os.path.dirname(__file__), "pc_backend", "fonts", "DejaVuSans.ttf")
]
fonte_encontrada = None
for fp in fontes_possiveis:
    if os.path.exists(fp):
        fonte_encontrada = fp
        break

print(f"[INFO] Fonte encontrada: {fonte_encontrada}")

if not fonte_encontrada:
    print("[ERRO] Nenhuma fonte TTF encontrada no sistema.")
    exit()

# 2. Substitui o uso de "Helvetica" pela fonte TTF nas rotas do BF e DFC
# Vamos localizar as funções gerar_pdf_analise_financeira_bf e gerar_pdf_analise_dfc

def injetar_fonte(bloco):
    """Adiciona add_font() e substitui Helvetica pela fonte, mantendo o estilo (B/I)."""
    # Insere add_font após o pdf.add_page() inicial (se existir)
    bloco = re.sub(
        r'(pdf\.add_page\(\))',
        r'\1\n    pdf.add_font("DejaVu", "", r"' + fonte_encontrada.replace('\\','/') + r'", uni=True)\n    pdf.add_font("DejaVu", "B", r"' + fonte_encontrada.replace('\\','/') + r'", uni=True)\n    pdf.add_font("DejaVu", "I", r"' + fonte_encontrada.replace('\\','/') + r'", uni=True)',
        bloco,
        count=1
    )
    # Substitui Helvetica -> DejaVu
    bloco = bloco.replace('"Helvetica"', '"DejaVu"')
    bloco = bloco.replace("'Helvetica'", "'DejaVu'")
    return bloco

# Localiza as funções do BF e DFC
for nome_funcao in ["gerar_pdf_analise_financeira_bf", "gerar_pdf_analise_dfc"]:
    padrao = re.compile(
        rf'(@app\.get\("/{nome_funcao}/[^"]*"\).*?)(?=\n@app\.|\Z)',
        re.DOTALL
    )
    match = padrao.search(main_code)
    if match:
        bloco = match.group(1)
        bloco_novo = injetar_fonte(bloco)
        main_code = main_code.replace(bloco, bloco_novo)
        print(f"[OK] Injetada fonte UTF-8 em {nome_funcao}.")
    else:
        print(f"[AVISO] Função {nome_funcao} não encontrada.")

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(main_code)
print("[OK] BF e DFC agora usam fonte TTF com suporte a UTF-8.")
