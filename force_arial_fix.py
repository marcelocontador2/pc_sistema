import re, shutil, datetime, ast, os

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_force_arial_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# 1. Verifica se arial.ttf existe na pasta backend
pasta_backend = r"pc_backend"
arial_path = os.path.join(pasta_backend, "arial.ttf")
arial_bold_path = os.path.join(pasta_backend, "arialbd.ttf")

if not os.path.exists(arial_path):
    # Tenta copiar do Windows
    win_arial = r"C:\Windows\Fonts\arial.ttf"
    if os.path.exists(win_arial):
        import shutil
        shutil.copy2(win_arial, arial_path)
        print(f"[OK] arial.ttf copiada para {arial_path}")
    else:
        print("[ERRO] arial.ttf nao encontrada no Windows")
else:
    print(f"[OK] arial.ttf ja existe ({os.path.getsize(arial_path)} bytes)")

if not os.path.exists(arial_bold_path):
    win_arial_bold = r"C:\Windows\Fonts\arialbd.ttf"
    if os.path.exists(win_arial_bold):
        import shutil
        shutil.copy2(win_arial_bold, arial_bold_path)
        print(f"[OK] arialbd.ttf copiada")

# 2. Força a fonte Arial no main.py (usa caminho absoluto)
# Primeiro, remove qualquer referência antiga a DejaVu
c = c.replace('DejaVuSans.ttf', 'arial.ttf')
c = c.replace('DejaVuSans-Bold.ttf', 'arialbd.ttf')
c = c.replace('"DejaVu"', '"ArialUnicode"')

# 3. Substitui o bloco de registro da fonte para garantir que Arial seja usada
# Procura o bloco onde a fonte é registrada
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
    print("[OK] Bloco de registro da fonte substituido por Arial")
else:
    print("[AVISO] Bloco de registro da fonte nao encontrado. Tentando abordagem alternativa...")
    # Tenta encontrar qualquer bloco que mencione add_font
    idx = c.find('pdf.add_font')
    if idx != -1:
        # Remove o bloco antigo (até a linha "fonte_padrao = ...")
        fim_bloco = c.find('fonte_padrao = ', idx)
        if fim_bloco != -1:
            fim_linha = c.find('\n', fim_bloco)
            c = c[:idx] + novo_bloco + c[fim_linha:]
            print("[OK] Bloco antigo substituido")

# 4. Garante que _limpar_ascii remove \f, \t, \v, \a
# Atualiza a função _limpar_ascii
nova_limpar = '''
def _limpar_ascii(txt):
    """Remove todos os caracteres não-ASCII e de controle para compatibilidade com FPDF/Helvetica."""
    if not txt: return ""
    s = str(txt)
    # Remove tabulacoes e caracteres de controle (incluindo \\f, \\t, \\v, \\a)
    s = s.replace("\\t", " ").replace("\\n", " ").replace("\\r", " ")
    s = s.replace("\\f", " ").replace("\\v", " ").replace("\\a", " ")
    s = s.replace(chr(12), " ").replace(chr(11), " ").replace(chr(7), " ")
    # Remove qualquer caractere fora do ASCII imprimivel (32-126)
    s = "".join(ch if 32 <= ord(ch) <= 126 else " " for ch in s)
    return s
'''

# Substitui a função _limpar_ascii existente
padrao_ascii = r'def _limpar_ascii\(txt\):.*?return s'
if re.search(padrao_ascii, c, re.DOTALL):
    c = re.sub(padrao_ascii, nova_limpar, c, flags=re.DOTALL)
    print("[OK] Funcao _limpar_ascii atualizada para remover \\f, \\t, \\v, \\a")

# 5. Garante que _limpar_pdf também remove esses caracteres
nova_limpar_pdf = '''
def _limpar_pdf(txt):
    """Limpa caracteres de controle, mantendo acentos (para fontes Unicode)."""
    if not txt: return ""
    s = str(txt)
    s = s.replace("\\t", " ").replace("\\n", " ").replace("\\r", " ")
    s = s.replace("\\f", " ").replace("\\v", " ").replace("\\a", " ")
    s = s.replace(chr(12), " ").replace(chr(11), " ").replace(chr(7), " ")
    s = "".join(ch if ord(ch) >= 32 else " " for ch in s)
    return s
'''

padrao_pdf = r'def _limpar_pdf\(txt\):.*?return s'
if re.search(padrao_pdf, c, re.DOTALL):
    c = re.sub(padrao_pdf, nova_limpar_pdf, c, flags=re.DOTALL)
    print("[OK] Funcao _limpar_pdf atualizada para remover \\f, \\t, \\v, \\a")

# 6. Salva
open(back_path, 'w', encoding='utf-8').write(c)

# Valida
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("\n[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"\n[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_force_arial_{ts}", back_path)
    print("[OK] Backup restaurado")
