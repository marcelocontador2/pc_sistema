import re, os

c = open('main.py', encoding='utf-8-sig').read()

print("=" * 70)
print("ROTAS RELACIONADAS A UPLOAD / IMPORT / COMPARATIVO")
print("=" * 70)

# Encontra todos os decorators @app.(post|get|put) e a assinatura da função seguinte
padrao = r'@app\.(post|get|put|delete)\(["\']([^"\']+)["\']\)\s*\ndef\s+(\w+)\([^)]*\)'

matches = list(re.finditer(padrao, c))
for m in matches:
    metodo, rota, func = m.group(1).upper(), m.group(2), m.group(3)
    if any(k in rota.lower() or k in func.lower() for k in ["upload", "import", "comparativ", "receit", "despes"]):
        print(f"  {metodo:6} {rota:55} -> {func}()")

print()
print("=" * 70)
print("FUNÇÕES QUE MENCIONAM 'COMPARATIVO_RECEITAS' NO CORPO")
print("=" * 70)

for m in matches:
    func = m.group(3)
    rota = m.group(2)
    metodo = m.group(1).upper()
    # Localiza o bloco da função (até a próxima def @app)
    inicio = m.end()
    prox = re.search(r'\n@app\.', c[inicio:])
    fim = inicio + prox.start() if prox else len(c)
    corpo = c[inicio:fim]
    if "COMPARATIVO_RECEITAS" in corpo.upper() or "comparativo_receitas" in corpo:
        print(f"\n--- {metodo} {rota} -> {func}() ---")
        print(f"  [tamanho do corpo: {len(corpo)} caracteres]")
        # Mostra as primeiras 40 linhas
        for ln in corpo.splitlines()[:40]:
            print(f"  {ln}")

print()
print("=" * 70)
print("HTMLs NA PASTA pc_frontend QUE MENCIONAM 'importar' OU 'receitas'")
print("=" * 70)

front_dir = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_frontend"
if os.path.exists(front_dir):
    for f in sorted(os.listdir(front_dir)):
        if f.endswith(".html"):
            caminho = os.path.join(front_dir, f)
            try:
                html = open(caminho, encoding="utf-8-sig").read()
            except:
                try:
                    html = open(caminho, encoding="latin-1").read()
                except:
                    continue
            low = html.lower()
            if ("importar" in low or "upload" in low) and ("receit" in low or "comparativ" in low):
                print(f"  {f}  ({len(html)} chars)")
