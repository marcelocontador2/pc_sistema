import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_encoding_fix_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# 1. Adiciona função para corrigir encoding duplo (UTF-8 lido como latin-1)
helper = '''
def _corrigir_encoding(txt):
    """Corrige encoding duplo (UTF-8 lido como latin-1)."""
    if not txt: return ""
    try:
        # Tenta decodificar como latin-1 e re-codificar como utf-8
        # Isso converte Ã§ -> ç, Ã£ -> ã, etc.
        s = txt.encode("latin-1", "ignore").decode("utf-8", "ignore")
        return s
    except:
        return txt

'''

# Adiciona após _limpar_ascii
if 'def _corrigir_encoding' not in c:
    idx_ascii = c.find('def _limpar_ascii')
    if idx_ascii != -1:
        idx_fim = c.find('\n\n', idx_ascii)
        if idx_fim == -1: idx_fim = idx_ascii + 500
        c = c[:idx_fim] + '\n' + helper + c[idx_fim:]
        print("[OK] Função _corrigir_encoding adicionada")

# 2. Aplica a correção no conteúdo do CSV antes de processar
# Localiza a leitura do CSV no download_pdf
# O trecho é: content = f.read()
c = c.replace(
    'content = f.read()',
    'content = _corrigir_encoding(f.read())'
)

# Mas isso só funciona se o CSV foi lido como latin-1
# Vamos garantir que a leitura seja latin-1 primeiro e depois corrigir
c = c.replace(
    'for enc in ["utf-8-sig", "latin-1"]:',
    'for enc in ["latin-1", "utf-8-sig"]:'  # latin-1 primeiro
)

print("[OK] Leitura do CSV prioriza latin-1 e aplica _corrigir_encoding")

# 3. Salva
open(back_path, 'w', encoding='utf-8').write(c)

# 4. Valida
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("\n[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"\n[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_encoding_fix_{ts}", back_path)
    print("[OK] Backup restaurado")
