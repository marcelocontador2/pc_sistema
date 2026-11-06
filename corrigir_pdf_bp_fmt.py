import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_pdf_bp_fmt_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Localiza a funcao do PDF do BP
idx = c.find('@app.get("/gerar_pdf_analise_bp/{id}")')
if idx == -1:
    print("[ERRO] Rota do PDF do BP nao encontrada.")
    exit(1)

fim = c.find('@app', idx + 10)
if fim == -1:
    fim = len(c)

bloco = c[idx:fim]

# 1. Corrige a funcao fmt (que divide por 1 milhao)
antigo_fmt = '''    def fmt(v):
        if v is None: return "0,00"
        return f"{(v/1000000):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")'''

novo_fmt = '''    def fmt(v):
        if v is None: return "0,00"
        return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")'''

if antigo_fmt in bloco:
    bloco = bloco.replace(antigo_fmt, novo_fmt)
    print("[OK] Funcao fmt corrigida: valores cheios (sem dividir por 1 milhao).")
else:
    print("[AVISO] Funcao fmt nao encontrada. Tentando variacao...")
    # Tenta encontrar qualquer fmt que use 1000000
    padrao_fmt = re.compile(r'def fmt\(v\):.*?return.*?1000000.*?\n', re.DOTALL)
    match = padrao_fmt.search(bloco)
    if match:
        bloco = bloco.replace(match.group(0), novo_fmt + "\n")
        print("[OK] Funcao fmt corrigida (variacao).")

# 2. Atualiza os cabecalhos da tabela (remove "R$ mi", coloca "R$")
bloco = bloco.replace('"2025 (R$ mi)"', '"Periodo Atual (R$)"')
bloco = bloco.replace('"2026 (R$ mi)"', '"Periodo Anterior (R$)"')
bloco = bloco.replace('"2025 (R$ mi)"', '"Periodo Atual (R$)"')
bloco = bloco.replace('"2026 (R$ mi)"', '"Periodo Anterior (R$)"')

c = c[:idx] + bloco + c[fim:]
open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] PDF do BP corrigido (valores cheios, sem cortar milhar).")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_pdf_bp_fmt_{ts}", back_path)
