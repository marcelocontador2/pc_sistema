import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_remove_old_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Regex para encontrar a rota antiga (/gerar_pdf_panorama/{id}) e apagar TUDO dela até o próximo @app
padrao_antigo = r'@app\.get\("/gerar_pdf_panorama/\{id\}"\)\s*async def gerar_pdf_panorama\(id: int\):.*?(?=\n@app\.|\Z)'

if re.search(padrao_antigo, c, flags=re.DOTALL):
    c = re.sub(padrao_antigo, '', c, flags=re.DOTALL)
    open(back_path, 'w', encoding='utf-8').write(c)
    print("[OK] Rota duplicada (antiga e bugada) REMOVIDA com sucesso!")
else:
    print("[AVISO] Não foi possível encontrar a rota antiga pelo padrão exato.")

# Validar sintaxe
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py 100% validada!")
except SyntaxError as e:
    print(f"[ERRO] Erro de sintaxe no main.py: {e}")
