import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_utf8_csv_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Localiza a função download_pdf e altera a leitura do CSV
inicio = c.find('async def download_pdf(')
if inicio == -1:
    print("[ERRO] Função não encontrada.")
    exit(1)

fim = c.find('@app.', inicio + 10)
if fim == -1: fim = len(c)

corpo = c[inicio:fim]

# A leitura atual:
# for enc in ["utf-8-sig", "utf-8", "latin-1"]:
#     try:
#         with open(csv_path, "r", encoding=enc) as f:
#             content = f.read()
#         break
#     except UnicodeDecodeError:
#         continue

# Nova leitura: prioriza latin-1 (que preserva os bytes originais) e depois limpa os caracteres corrompidos
novo_corpo = corpo.replace(
    '''        content = ""
        for enc in ["utf-8-sig", "utf-8", "latin-1"]:
            try:
                with open(csv_path, "r", encoding=enc) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue''',
    '''        # Leitura robusta: tenta utf-8-sig, depois latin-1 (que aceita qualquer byte)
        content = ""
        for enc in ["utf-8-sig", "latin-1"]:
            try:
                with open(csv_path, "r", encoding=enc) as f:
                    content = f.read()
                break
            except:
                continue
        
        # Corrige caracteres corrompidos (ex: Ã§ -> ç, Ã£ -> ã)
        content = content.replace("Ã§", "ç").replace("Ã£", "ã").replace("Ã¡", "á")
        content = content.replace("Ã©", "é").replace("Ã­", "í").replace("Ã³", "ó")
        content = content.replace("Ãº", "ú").replace("Ã¢", "â").replace("Ãª", "ê")
        content = content.replace("Ã´", "ô").replace("Ãª", "ê").replace("Ã§", "ç")
        content = content.replace("Ãƒ", "Ã").replace("Ã‰", "É").replace("Ã“", "Ó")'''
)

if novo_corpo != corpo:
    c = c[:inicio] + novo_corpo + c[fim:]
    open(back_path, 'w', encoding='utf-8').write(c)
    print("[OK] Função download_pdf atualizada com correção de encoding!")
else:
    print("[AVISO] Trecho de leitura do CSV não encontrado. Tentando outra abordagem...")

# Valida sintaxe
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_utf8_csv_{ts}", back_path)
    print("[OK] Backup restaurado")
