import re

ARQUIVO = r"pc_backend\main.py"

with open(ARQUIVO, "r", encoding="utf-8") as f:
    content = f.read()
lines = content.split("\n")

print(f"Arquivo: {ARQUIVO}  ({len(content):,} chars)\n")

print("=== 1) Função _calc_liquidez / calc_liquidez ===")
found = False
for m in re.finditer(r'def\s+_?calc_liquidez\s*\([^)]*\).*?(?=\ndef\s|\Z)', content, re.DOTALL):
    print(m.group(0)[:4000]); print("---"); found = True
if not found:
    print("(NÃO ENCONTRADA)")

print("\n=== 2) Linhas que mencionam 'liquidez' ===")
for i, line in enumerate(lines, 1):
    if "liquidez" in line.lower():
        print(f"{i}: {line.rstrip()}")

print("\n=== 3) CREATE TABLE com liquidez ===")
for m in re.finditer(r'CREATE TABLE[^;]*liquidez[^;]*;', content, re.IGNORECASE | re.DOTALL):
    print(m.group(0)); print("---")

print("\n=== 4) Blocos das rotas de análise patrimonial (padrão) ===")
for path in ["/api/analise_patrimonial/", "/historico_analise_patrimonial",
             "/gerar_pdf_analise_patrimonial/", "/excluir_analise_patrimonial/",
             "/salvar_analise_patrimonial/"]:
    idx = content.find(f'"{path}')
    if idx == -1:
        idx = content.find(f"'{path}")
    if idx != -1:
        start = content.rfind("@app.", 0, idx)
        end = content.find("\n@app.", idx)
        print(f"\n>>> {path}")
        print(content[start:end if end != -1 else idx+1200][:1500])

print("\n=== 5) Função _calc_patrimonial (referência) ===")
for m in re.finditer(r'def\s+_?calc_patrimonial\s*\([^)]*\).*?(?=\ndef\s|\Z)', content, re.DOTALL):
    print(m.group(0)[:3500]); print("---")

print("\n=== 6) Instância FastAPI ===")
for m in re.finditer(r'(\w+)\s*=\s*FastAPI\s*\(', content):
    print("  instância:", m.group(1))

print("\n=== 7) Rota /liquidez (que serve o HTML) ===")
for m in re.finditer(r'@\w+\.get\(\s*["\']/liquidez["\'][^)]*\)', content):
    print(m.group(0))
    idx = m.end()
    print(content[idx:idx+600])
    print("---")
