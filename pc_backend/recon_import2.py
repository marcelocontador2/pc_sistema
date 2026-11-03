import re, os

c = open('main.py', encoding='utf-8-sig').read()

print("=" * 70)
print("TODAS AS ROTAS POST DO main.py")
print("=" * 70)
for m in re.finditer(r'@app\.post\(["\']([^"\']+)["\']\)\s*\ndef\s+(\w+)\(([^)]*)\)', c):
    print(f"  POST {m.group(1):55} -> {m.group(2)}({m.group(3)[:60]})")

print()
print("=" * 70)
print("ONDE SE ESCREVE EM uploads_raw (open(...,'w') ou shutil.copy)")
print("=" * 70)
# Procura blocos de função que mencionam uploads_raw E escrita
for m in re.finditer(r'@app\.(post|get)\(["\']([^"\']+)["\']\)\s*\ndef\s+(\w+)\([^)]*\)', c):
    inicio = m.end()
    prox = re.search(r'\n@app\.', c[inicio:])
    fim = inicio + prox.start() if prox else len(c)
    corpo = c[inicio:fim]
    if "uploads_raw" in corpo:
        tem_write = any(k in corpo for k in ['"w"', "'w'", "shutil.copy", "file.save", "write_bytes", "UploadFile"])
        if tem_write:
            print(f"\n--- {m.group(1).upper()} {m.group(2)} -> {m.group(3)}() ---")
            for ln in corpo.splitlines()[:80]:
                print(f"  {ln}")

print()
print("=" * 70)
print("importar.html — CHAMADAS FETCH/POST E ELEMENTOS <input type=file>")
print("=" * 70)
html_path = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_frontend\importar.html"
if os.path.exists(html_path):
    h = open(html_path, encoding="utf-8-sig").read()
    print(f"[tamanho: {len(h)} chars]\n")
    # Mostra todas as chamadas fetch
    for m in re.finditer(r'fetch\(([^)]+)\)', h):
        print(f"  fetch({m.group(1)[:120]})")
    print()
    # Mostra inputs file e seus contextos
    for m in re.finditer(r'<input[^>]*type=["\']file["\'][^>]*>', h):
        print(f"  {m.group(0)}")
    print()
    # Mostra selects / options de "tipo de relatorio"
    for m in re.finditer(r'<select[^>]*id=["\']([^"\']+)["\'][^>]*>(.*?)</select>', h, re.DOTALL):
        sid = m.group(1)
        opts = re.findall(r'<option[^>]*value=["\']([^"\']*)["\'][^>]*>([^<]*)</option>', m.group(2))
        print(f"  <select id='{sid}'>:")
        for v, lbl in opts:
            print(f"      value='{v}' -> {lbl.strip()}")
