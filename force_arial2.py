import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_force2_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# 1. Corrige o bloco de registro da fonte para usar Arial (não DejaVu)
padrao_bloco = r'# Registra fonte Unicode.*?fonte_padrao = "Helvetica"'
novo_bloco = '''# Registra fonte Arial (sempre existe no Windows)
        import os
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arial.ttf")
        font_bold_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arialbd.ttf")
        
        if os.path.exists(font_path):
            try:
                pdf.add_font("ArialUnicode", "", font_path, uni=True)
                if os.path.exists(font_bold_path):
                    pdf.add_font("ArialUnicode", "B", font_bold_path, uni=True)
                else:
                    pdf.add_font("ArialUnicode", "B", font_path, uni=True)
                fonte_padrao = "ArialUnicode"
                print("[INFO] Fonte Arial registrada com sucesso")
            except Exception as e:
                print(f"[AVISO] Erro ao registrar Arial: {e}")
                fonte_padrao = "Helvetica"
        else:
            fonte_padrao = "Helvetica"
            print("[AVISO] Fonte Arial nao encontrada, usando Helvetica")'''

if re.search(padrao_bloco, c, re.DOTALL):
    c = re.sub(padrao_bloco, novo_bloco, c, flags=re.DOTALL)
    print("[OK] Bloco de fonte substituido por Arial")
else:
    print("[AVISO] Bloco de fonte nao encontrado")

# 2. Corrige a _limpar_pdf para remover \f, \v, \a e chr(12), chr(11), chr(7)
nova_limpar_pdf = '''
def _limpar_pdf(txt):
    """Limpa caracteres de controle, mantendo acentos (para fontes Unicode)."""
    if not txt: return ""
    s = str(txt)
    # Remove caracteres de controle explicitamente
    s = s.replace("\\t", " ").replace("\\n", " ").replace("\\r", " ")
    s = s.replace("\\f", " ").replace("\\v", " ").replace("\\a", " ")
    s = s.replace(chr(12), " ").replace(chr(11), " ").replace(chr(7), " ")
    # Remove qualquer caractere fora do ASCII imprimivel OU mantem acentos (latin-1)
    s = "".join(ch if (ord(ch) >= 32 and ord(ch) < 256) else " " for ch in s)
    return s
'''

padrao_pdf = r'def _limpar_pdf\(txt\):.*?return s'
if re.search(padrao_pdf, c, re.DOTALL):
    c = re.sub(padrao_pdf, nova_limpar_pdf, c, flags=re.DOTALL)
    print("[OK] Funcao _limpar_pdf corrigida para remover \\f, \\v, \\a")

# 3. Garante que _limpar_ascii também remove \f
nova_limpar_ascii = '''
def _limpar_ascii(txt):
    """Remove todos os caracteres não-ASCII e de controle para compatibilidade com FPDF/Helvetica."""
    if not txt: return ""
    s = str(txt)
    s = s.replace("\\t", " ").replace("\\n", " ").replace("\\r", " ")
    s = s.replace("\\f", " ").replace("\\v", " ").replace("\\a", " ")
    s = s.replace(chr(12), " ").replace(chr(11), " ").replace(chr(7), " ")
    s = "".join(ch if 32 <= ord(ch) <= 126 else " " for ch in s)
    return s
'''

padrao_ascii = r'def _limpar_ascii\(txt\):.*?return s'
if re.search(padrao_ascii, c, re.DOTALL):
    c = re.sub(padrao_ascii, nova_limpar_ascii, c, flags=re.DOTALL)
    print("[OK] Funcao _limpar_ascii corrigida para remover \\f")

# 4. Substitui _limpar_pdf por _limpar_ascii nas células do download_pdf (para garantir compatibilidade)
# Mas só se a fonte for Helvetica (fallback)
# Vou fazer uma substituição condicional: sempre usa _limpar_ascii (mais seguro)

# Substitui todas as chamadas _limpar_pdf nas células por _limpar_ascii
# (mantém a função _limpar_pdf para outros usos)
c = c.replace('_limpar_pdf(h)', '_limpar_ascii(h)')
c = c.replace('_limpar_pdf(txt)', '_limpar_ascii(txt)')
c = c.replace('_limpar_pdf(titulo_pdf)', '_limpar_ascii(titulo_pdf)')
c = c.replace('_limpar_pdf(f"Periodo: {periodo_formatado}")', '_limpar_ascii(f"Periodo: {periodo_formatado}")')
c = c.replace('_limpar_pdf(f"COFEN/BR - {titulo_pdf} - Periodo: {periodo_formatado} (Continuacao)")', 
              '_limpar_ascii(f"COFEN/BR - {titulo_pdf} - Periodo: {periodo_formatado} (Continuacao)")')

print("[OK] Chamadas _limpar_pdf substituidas por _limpar_ascii nas celulas")

# 5. Salva
open(back_path, 'w', encoding='utf-8').write(c)

# Valida
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("\n[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"\n[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_force2_{ts}", back_path)
    print("[OK] Backup restaurado")
