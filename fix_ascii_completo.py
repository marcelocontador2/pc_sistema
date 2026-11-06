import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_ascii_fix_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# 1. Adiciona função auxiliar de limpeza no topo do arquivo (após imports)
helper = '''
def _limpar_ascii(txt):
    """Remove todos os caracteres não-ASCII de um texto para compatibilidade com FPDF/Helvetica."""
    if not txt: return ""
    s = str(txt)
    # Substitui tabulações e caracteres de controle
    s = s.replace("\\t", " ").replace("\\n", " ").replace("\\r", " ")
    # Tenta decodificar latin-1 primeiro (mais compatível)
    try:
        s = s.encode("latin-1", "replace").decode("latin-1")
    except:
        pass
    # Remove qualquer caractere fora do ASCII imprimível (32-126)
    s = "".join(ch if 32 <= ord(ch) <= 126 else " " for ch in s)
    return s

'''

# Insere o helper após os imports (procura a primeira linha "from" ou "import")
linhas = c.split('\n')
for i, ln in enumerate(linhas):
    if ln.strip().startswith('from ') or ln.strip().startswith('import '):
        # Insere após o último import consecutivo
        j = i
        while j + 1 < len(linhas) and (linhas[j+1].strip().startswith('from ') or linhas[j+1].strip().startswith('import ')):
            j += 1
        linhas.insert(j + 1, helper)
        break
c = '\n'.join(linhas)
print("[OK] Função _limpar_ascii adicionada")

# 2. Substitui TODAS as chamadas de pdf.cell e pdf.multi_cell para usar _limpar_ascii
# Padrão: pdf.cell(LARGURA, ALTURA, TEXTO, ...)
# Substitui o TEXTO por _limpar_ascii(TEXTO)

# 2.1 pdf.cell(0, 6, "COFEN/BR - ...", ...)
c = c.replace(
    'pdf.cell(0, 6, "COFEN/BR - Conselho Federal de Enfermagem"',
    'pdf.cell(0, 6, _limpar_ascii("COFEN/BR - Conselho Federal de Enfermagem")'
)

# 2.2 pdf.cell(0, 5, "CNPJ: ...", ...)
c = c.replace(
    'pdf.cell(0, 5, "CNPJ: 47.217.146/0001-57"',
    'pdf.cell(0, 5, _limpar_ascii("CNPJ: 47.217.146/0001-57")'
)

# 2.3 pdf.cell(85, 6, f"Período: {periodo_formatado}", ...)
c = c.replace(
    'pdf.cell(85, 6, f"Período: {periodo_formatado}"',
    'pdf.cell(85, 6, _limpar_ascii(f"Período: {periodo_formatado}")'
)

# 2.4 pdf.cell(85, 5, titulo_pdf, ...)
c = c.replace(
    'pdf.cell(85, 5, titulo_pdf',
    'pdf.cell(85, 5, _limpar_ascii(titulo_pdf)'
)

# 2.5 pdf.cell(0, 5, f"COFEN/BR - {titulo_pdf} - Período: {periodo_formatado} (Continuação)", ...)
c = c.replace(
    'pdf.cell(0, 5, f"COFEN/BR - {titulo_pdf} - Período: {periodo_formatado} (Continuação)"',
    'pdf.cell(0, 5, _limpar_ascii(f"COFEN/BR - {titulo_pdf} - Período: {periodo_formatado} (Continuação)")'
)

# 2.6 pdf.multi_cell(col_w[j], 4, h, ...)
c = c.replace(
    'pdf.multi_cell(col_w[j], 4, h, border=0, align="C")',
    'pdf.multi_cell(col_w[j], 4, _limpar_ascii(h), border=0, align="C")'
)

# 2.7 pdf.multi_cell(col_w[j], 5, txt, ...) - no draw_row
c = c.replace(
    'pdf.multi_cell(col_w[j], 5, txt, border=0, align="L")',
    'pdf.multi_cell(col_w[j], 5, _limpar_ascii(txt), border=0, align="L")'
)

# 2.8 pdf.cell(col_w[j], 5, txt, align="R", border=0) - no draw_row
c = c.replace(
    'pdf.cell(col_w[j], 5, txt, align="R", border=0)',
    'pdf.cell(col_w[j], 5, _limpar_ascii(txt), align="R", border=0)'
)

# 3. Substitui as limpezas manuais dentro do draw_row por _limpar_ascii
# Para não duplicar, mantém apenas a chamada _limpar_ascii no final
c = c.replace(
    """txt_raw = str(row[j])
                    txt_raw = txt_raw.replace(chr(9), ' ').replace(chr(10), ' ').replace(chr(13), ' ')
                    txt_raw = ''.join(ch if ord(ch) >= 32 else ' ' for ch in txt_raw)
                    txt = txt_raw.encode('latin-1', 'replace').decode('latin-1') or " \"""",
    'txt = _limpar_ascii(row[j]) or " "'
)

c = c.replace(
    """txt_raw = str(row[j])
                txt_raw = txt_raw.replace(chr(9), ' ').replace(chr(10), ' ').replace(chr(13), ' ')
                txt_raw = ''.join(ch if ord(ch) >= 32 else ' ' for ch in txt_raw)
                txt = txt_raw.encode('latin-1', 'replace').decode('latin-1')""",
    'txt = _limpar_ascii(row[j])'
)

# Salva
open(back_path, 'w', encoding='utf-8').write(c)

# Valida
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_ascii_fix_{ts}", back_path)
    print("[OK] Backup restaurado")

print("\n[OK] Todas as escritas no PDF agora passam por _limpar_ascii().")
