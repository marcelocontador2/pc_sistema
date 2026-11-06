import re, shutil, datetime, ast, os

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_dejavu_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# 1. Localiza o início da função download_pdf
inicio = c.find('async def download_pdf(')
if inicio == -1:
    print("[ERRO] Função não encontrada.")
    exit(1)

# 2. Adiciona o registro da fonte DejaVu logo após a criação do PDF
# (a linha "pdf = FPDF(...)" existe no corpo)
ancora = 'pdf = FPDF(orientation="L", unit="mm", format="A4")'
if ancora in c:
    # Adiciona o registro da fonte após a criação
    novo_bloco = '''pdf = FPDF(orientation="L", unit="mm", format="A4")
        # Registra fonte Unicode (DejaVu Sans) para suportar acentos
        import os
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DejaVuSans.ttf")
        font_bold_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DejaVuSans-Bold.ttf")
        
        # Se não existir no backend, tenta copiar do Windows
        if not os.path.exists(font_path):
            win_fonts = ["C:\\\\Windows\\\\Fonts\\\\DejaVuSans.ttf", "C:\\\\Windows\\\\Fonts\\\\DejaVuSans-Bold.ttf"]
            if os.path.exists(win_fonts[0]):
                import shutil
                shutil.copy2(win_fonts[0], font_path)
                if os.path.exists(win_fonts[1]):
                    shutil.copy2(win_fonts[1], font_bold_path)
        
        if os.path.exists(font_path):
            pdf.add_font("DejaVu", "", font_path, uni=True)
            if os.path.exists(font_bold_path):
                pdf.add_font("DejaVu", "B", font_bold_path, uni=True)
            else:
                pdf.add_font("DejaVu", "B", font_path, uni=True)
            fonte_padrao = "DejaVu"
            print("[INFO] Fonte DejaVu registrada com sucesso")
        else:
            fonte_padrao = "Helvetica"
            print("[AVISO] Fonte DejaVu não encontrada, usando Helvetica")'''
    
    c = c.replace(ancora, novo_bloco, 1)
    print("[OK] Registro da fonte DejaVu adicionado")
else:
    print("[AVISO] Âncora 'pdf = FPDF(...)' não encontrada")

# 3. Substitui TODAS as chamadas set_font("Helvetica", ...) por set_font(fonte_padrao, ...)
# Mas primeiro precisamos declarar fonte_padrao antes do uso
c = c.replace('pdf = FPDF(orientation="L", unit="mm", format="A4")', 
              'pdf = FPDF(orientation="L", unit="mm", format="A4")\n        fonte_padrao = "Helvetica"', 1)

# Agora substitui as chamadas
c = re.sub(
    r'pdf\.set_font\("Helvetica",\s*("B"|"I"|"")\s*,\s*(\d+(?:\.\d+)?)\)',
    r'pdf.set_font(fonte_padrao, \1, \2)',
    c
)
print("[OK] Chamadas set_font substituídas por fonte_padrao")

# 4. Remove a _limpar_ascii dos textos que vão pro PDF (mantém só a limpeza de tab)
# Mas mantém a função _limpar_ascii para outros usos
# Substitui as chamadas _limpar_ascii(txt) por _limpar_ascii_sem_acento(txt) nas células
# (precisamos criar uma versão que mantém acentos)

# Cria a função _limpar_pdf que mantém acentos
helper = '''
def _limpar_pdf(txt):
    """Limpa apenas tabulações e caracteres de controle, mantendo acentos."""
    if not txt: return ""
    s = str(txt)
    s = s.replace("\\t", " ").replace("\\n", " ").replace("\\r", " ")
    s = "".join(ch if ord(ch) >= 32 else " " for ch in s)
    return s
'''

# Adiciona após _limpar_ascii
if 'def _limpar_pdf' not in c:
    idx_ascii = c.find('def _limpar_ascii')
    if idx_ascii != -1:
        # Encontra o fim da função _limpar_ascii
        idx_fim = c.find('\n\n', idx_ascii)
        if idx_fim == -1: idx_fim = idx_ascii + 500
        c = c[:idx_fim] + '\n' + helper + c[idx_fim:]
        print("[OK] Função _limpar_pdf adicionada (mantém acentos)")

# 5. Substitui as chamadas _limpar_ascii por _limpar_pdf nos textos do PDF
c = c.replace('_limpar_ascii(h)', '_limpar_pdf(h)')
c = c.replace('_limpar_ascii(txt)', '_limpar_pdf(txt)')
c = c.replace('_limpar_ascii(titulo_pdf)', '_limpar_pdf(titulo_pdf)')
c = c.replace('_limpar_ascii(f"Periodo: {periodo_formatado}")', '_limpar_pdf(f"Periodo: {periodo_formatado}")')
c = c.replace('_limpar_ascii(f"COFEN/BR - {titulo_pdf} - Periodo: {periodo_formatado} (Continuacao)")', 
              '_limpar_pdf(f"COFEN/BR - {titulo_pdf} - Periodo: {periodo_formatado} (Continuacao)")')
c = c.replace('_limpar_ascii("COFEN/BR - Conselho Federal de Enfermagem")', '"COFEN/BR - Conselho Federal de Enfermagem"')
c = c.replace('_limpar_ascii("CNPJ: 47.217.146/0001-57")', '"CNPJ: 47.217.146/0001-57"')

print("[OK] Chamadas _limpar_ascii substituídas por _limpar_pdf nos textos do PDF")

# 6. Salva
open(back_path, 'w', encoding='utf-8').write(c)

# Valida
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("\n[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"\n[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_dejavu_{ts}", back_path)
    print("[OK] Backup restaurado")
