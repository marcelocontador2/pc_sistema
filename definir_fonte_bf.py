import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_fonte_var_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Localiza a funcao do PDF do BF
idx = c.find('async def gerar_pdf_analise_financeira_bf(id: int):')
if idx == -1:
    print("[ERRO] Funcao nao encontrada.")
    exit(1)

# Encontra a proxima linha 'try:' ou o inicio do corpo da funcao
# Vamos inserir a definicao logo apos a linha 'async def ...:'
fim_assinatura = c.find('\n', idx) + 1

# Verifica se ja existe a definicao para nao duplicar
trecho = c[idx:idx+500]
if 'fonte_padrao = ' not in trecho:
    # Injeta a linha de definicao (mesma indentacao de 4 espacos)
    definicao = '    fonte_padrao = "Helvetica"\n'
    c = c[:fim_assinatura] + definicao + c[fim_assinatura:]
    print("[OK] Variavel 'fonte_padrao' definida como 'Helvetica' dentro da rota do PDF do BF.")
else:
    print("[AVISO] Variavel ja definida.")

open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_fonte_var_{ts}", back_path)
    print("[OK] Backup restaurado.")
