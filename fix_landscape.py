import re, shutil, datetime

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_fix_landscape_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    codigo = f.read()

# Localiza a função gerar_pdf_relatorio_consolidado
idx_rota = codigo.find("def gerar_pdf_relatorio_consolidado")
if idx_rota == -1:
    print("[ERRO] Função não encontrada.")
    exit()

fim_rota = codigo.find("\n@app.", idx_rota)
if fim_rota == -1:
    fim_rota = idx_rota + 3000

bloco = codigo[idx_rota:fim_rota]

# Substitui a chamada do page.pdf para usar landscape=False
bloco_antigo = bloco
bloco = bloco.replace(
    'orientation="portrait",\n            print_background=True,',
    'landscape=False,\n            print_background=True,'
)

if bloco != bloco_antigo:
    codigo = codigo.replace(bloco_antigo, bloco)
    print("[OK] Parâmetro 'orientation' substituído por 'landscape=False'.")
else:
    print("[AVISO] Não foi possível encontrar a linha exata para substituir. Tentando alternativa...")
    # Tenta outra variação
    bloco = bloco.replace('orientation="portrait"', 'landscape=False')
    codigo = codigo.replace(bloco_antigo, bloco)
    print("[OK] Substituição aplicada via alternativa.")

try:
    compile(codigo, arq_main, "exec")
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO SINTAXE] linha {e.lineno}: {e.msg}")
    exit()

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(codigo)
print("[OK] main.py salvo.")
