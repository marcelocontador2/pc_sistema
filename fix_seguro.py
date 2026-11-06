import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_seguro_{ts}")

# Lê o arquivo como texto puro
c = open(back_path, encoding='utf-8-sig').read()

# 1. Substitui o bloco de fonte (DejaVu → Arial) de forma segura
# Remove o bloco antigo inteiro (do comentário até "fonte_padrao = ")
inicio_bloco = c.find('# Registra fonte Unicode')
if inicio_bloco == -1:
    inicio_bloco = c.find('font_path = os.path.join')

if inicio_bloco != -1:
    # Encontra o fim do bloco: "print(\"[AVISO] Fonte ... Helvetica\")"
    fim_bloco = c.find('print("[AVISO] Fonte', inicio_bloco)
    if fim_bloco == -1:
        fim_bloco = c.find('fonte_padrao = "Helvetica"', inicio_bloco)
    
    if fim_bloco != -1:
        # Pega até o final da linha do print
        fim_linha = c.find('\n', fim_bloco)
        if fim_linha == -1:
            fim_linha = len(c)
        
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
        
        c = c[:inicio_bloco] + novo_bloco + c[fim_linha:]
        print("[OK] Bloco de fonte substituido por Arial")

# 2. Substitui a função _limpar_pdf por uma versão que remove \f (linha por linha)
# Encontra a função atual
padrao_pdf = r'def _limpar_pdf\(txt\):.*?return s'
match = re.search(padrao_pdf, c, re.DOTALL)
if match:
    nova_func = '''def _limpar_pdf(txt):
    """Limpa caracteres de controle, mantendo acentos (para fontes Unicode)."""
    if not txt: return ""
    s = str(txt)
    s = s.replace("\\\\t", " ").replace("\\\\n", " ").replace("\\\\r", " ")
    s = s.replace("\\\\f", " ").replace("\\\\v", " ").replace("\\\\a", " ")
    s = s.replace(chr(12), " ").replace(chr(11), " ").replace(chr(7), " ")
    s = "".join(ch if (ord(ch) >= 32 and ord(ch) < 256) else " " for ch in s)
    return s'''
    c = c[:match.start()] + nova_func + c[match.end():]
    print("[OK] Funcao _limpar_pdf corrigida")

# 3. Substitui a função _limpar_ascii
padrao_ascii = r'def _limpar_ascii\(txt\):.*?return s'
match_ascii = re.search(padrao_ascii, c, re.DOTALL)
if match_ascii:
    nova_func_ascii = '''def _limpar_ascii(txt):
    """Remove todos os caracteres não-ASCII e de controle."""
    if not txt: return ""
    s = str(txt)
    s = s.replace("\\\\t", " ").replace("\\\\n", " ").replace("\\\\r", " ")
    s = s.replace("\\\\f", " ").replace("\\\\v", " ").replace("\\\\a", " ")
    s = s.replace(chr(12), " ").replace(chr(11), " ").replace(chr(7), " ")
    s = "".join(ch if 32 <= ord(ch) <= 126 else " " for ch in s)
    return s'''
    c = c[:match_ascii.start()] + nova_func_ascii + c[match_ascii.end():]
    print("[OK] Funcao _limpar_ascii corrigida")

# 4. Substitui as chamadas nas células de _limpar_pdf para _limpar_ascii
# (linha por linha, para evitar problemas)
c = c.replace('_limpar_pdf(h)', '_limpar_ascii(h)')
c = c.replace('_limpar_pdf(txt)', '_limpar_ascii(txt)')
c = c.replace('_limpar_pdf(titulo_pdf)', '_limpar_ascii(titulo_pdf)')
c = c.replace('_limpar_pdf(f"Periodo: {periodo_formatado}")', '_limpar_ascii(f"Periodo: {periodo_formatado}")')
c = c.replace('_limpar_pdf(f"COFEN/BR - {titulo_pdf} - Periodo: {periodo_formatado} (Continuacao)")',
              '_limpar_ascii(f"COFEN/BR - {titulo_pdf} - Periodo: {periodo_formatado} (Continuacao)")')
print("[OK] Chamadas substituidas")

# 5. Salva
open(back_path, 'w', encoding='utf-8').write(c)

# 6. Valida
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("\n[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"\n[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_seguro_{ts}", back_path)
    print("[OK] Backup restaurado")
