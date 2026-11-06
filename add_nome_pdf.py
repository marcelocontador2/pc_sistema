import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_nome_pdf_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Localiza a função download_pdf
inicio = c.find('async def download_pdf(')
if inicio == -1:
    print("[ERRO] Função download_pdf não encontrada.")
    exit(1)

fim = c.find('@app.', inicio + 10)
if fim == -1: fim = len(c)

corpo = c[inicio:fim]

# Localiza o draw_header (que já tem acesso ao csv_path)
# Procura a função "def draw_header"
idx_draw = corpo.find('def draw_header(')
if idx_draw == -1:
    print("[ERRO] draw_header não encontrada dentro de download_pdf.")
    exit(1)

# Vamos inserir o nome do arquivo no rodapé de cada página do PDF
# A forma mais segura: adicionar depois do cabeçalho (linha 84 do draw_header: pdf.ln(12))
# Mas o draw_header não tem o caminho do arquivo. Vou usar uma variável global.
# Melhor: adicionar no final da geração do PDF (antes do return) um rodapé com o nome.

# Localiza o final da função (antes do return)
idx_out = corpo.find('out = pdf.output()')
if idx_out == -1:
    print("[ERRO] out = pdf.output() não encontrado.")
    exit(1)

# Insere o rodapé com o nome do arquivo em TODAS as páginas
# FPDF permite adicionar no loop de páginas: pdf.pages
# Vou adicionar um código que percorre as páginas e escreve o nome do arquivo no rodapé de cada uma

novo_codigo = '''        # Adiciona o nome do arquivo no rodapé de todas as páginas
        nome_arquivo_csv = os.path.basename(csv_path)
        for page_num in range(1, pdf.page_no() + 1):
            pdf.page = page_num
            pdf.set_y(-15)  # Posição do rodapé
            pdf.set_font("Helvetica", "I", 7)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 5, f"Arquivo: {nome_arquivo_csv}", align="C")
        
'''

# Substitui a linha 'out = pdf.output()' pelo novo código + out
if 'out = pdf.output()' in corpo:
    corpo_novo = corpo.replace('out = pdf.output()', novo_codigo + '        out = pdf.output()', 1)
    c = c[:inicio] + corpo_novo + c[fim:]
    open(back_path, 'w', encoding='utf-8').write(c)
    print("[OK] Nome do arquivo adicionado no rodapé de todas as páginas do PDF!")
else:
    print("[ERRO] Não foi possível substituir 'out = pdf.output()'.")

# Valida
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_nome_pdf_{ts}", back_path)
    print("[OK] Backup restaurado")
