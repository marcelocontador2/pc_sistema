import os, shutil, datetime, re, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_italic_{ts}")

# 1. Copia ariali.ttf (itálico) para a pasta backend
pasta_backend = r"pc_backend"
arial_italic_src = r"C:\Windows\Fonts\ariali.ttf"
arial_italic_dst = os.path.join(pasta_backend, "ariali.ttf")

if os.path.exists(arial_italic_src):
    shutil.copy2(arial_italic_src, arial_italic_dst)
    print(f"[OK] ariali.ttf copiada para {arial_italic_dst}")
else:
    print("[AVISO] ariali.ttf nao encontrada no Windows")

# 2. Atualiza o bloco de registro da fonte para incluir Itálico
c = open(back_path, encoding='utf-8-sig').read()

# Localiza o bloco de registro da fonte
inicio_bloco = c.find('# Registra fonte Arial')
if inicio_bloco == -1:
    inicio_bloco = c.find('font_path = os.path.join')

if inicio_bloco != -1:
    # Encontra o fim do bloco (até "fonte_padrao = \"Helvetica\"")
    fim_bloco = c.find('print("[AVISO] Fonte Arial nao encontrada', inicio_bloco)
    if fim_bloco == -1:
        fim_bloco = c.find('fonte_padrao = "Helvetica"', inicio_bloco)
    
    if fim_bloco != -1:
        # Pega até o final da linha
        fim_linha = c.find('\n', fim_bloco)
        if fim_linha == -1:
            fim_linha = len(c)
        
        novo_bloco = '''# Registra fonte Arial (regular, bold e italic)
        import os
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arial.ttf")
        font_bold_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arialbd.ttf")
        font_italic_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ariali.ttf")
        
        if os.path.exists(font_path):
            try:
                pdf.add_font("ArialUnicode", "", font_path, uni=True)
                if os.path.exists(font_bold_path):
                    pdf.add_font("ArialUnicode", "B", font_bold_path, uni=True)
                else:
                    pdf.add_font("ArialUnicode", "B", font_path, uni=True)
                if os.path.exists(font_italic_path):
                    pdf.add_font("ArialUnicode", "I", font_italic_path, uni=True)
                else:
                    pdf.add_font("ArialUnicode", "I", font_path, uni=True)
                fonte_padrao = "ArialUnicode"
                print("[INFO] Fonte Arial registrada com sucesso (regular, bold, italic)")
            except Exception as e:
                print(f"[AVISO] Erro ao registrar Arial: {e}")
                fonte_padrao = "Helvetica"
        else:
            fonte_padrao = "Helvetica"
            print("[AVISO] Fonte Arial nao encontrada, usando Helvetica")'''
        
        c = c[:inicio_bloco] + novo_bloco + c[fim_linha:]
        print("[OK] Bloco de fonte atualizado com Italic")

# 3. Salva
open(back_path, 'w', encoding='utf-8').write(c)

# 4. Valida
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("\n[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"\n[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_italic_{ts}", back_path)
    print("[OK] Backup restaurado")
