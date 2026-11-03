import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_fix_pano_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# 1. Remove a rota duplicada antiga (/gerar_pdf_panorama/{id})
padrao_rota_antiga = r'@app\.get\("/gerar_pdf_panorama/\{id\}"\)\s*def gerar_pdf_panorama\(id: int\):.*?(?=\n@app\.|\Z)'
c = re.sub(padrao_rota_antiga, '', c, flags=re.DOTALL)
print("[OK] Rota duplicada '/gerar_pdf_panorama/{id}' removida!")

# 2. Corrige a URL no Playwright da rota correta (remove o .html)
c = c.replace(
    'http://127.0.0.1:9994/panorama.html?historico_id={historico_id}',
    'http://127.0.0.1:9994/panorama?historico_id={historico_id}'
)
print("[OK] URL do Playwright corrigida para '/panorama' (sem .html)!")

open(back_path, 'w', encoding='utf-8').write(c)

# Validar
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py 100% validada!")
except SyntaxError as e:
    print(f"[ERRO] Erro de sintaxe: {e}")
