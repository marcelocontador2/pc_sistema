from pathlib import Path
import re

arquivo = Path("pc_frontend/custo_pessoal_pdf_completo.html")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Todos os IDs do HTML
ids_html = re.findall(r'id="([^"]+)"', conteudo)
print("=== IDs NO HTML ===")
for i in sorted(set(ids_html)):
    print(f"  {i}")

# 2. Todos os IDs que o JS atualiza
ids_js = re.findall(r"getElementById\('([^']+)'\)", conteudo)
print("\n=== IDs QUE O JS ATUALIZA ===")
for i in sorted(set(ids_js)):
    print(f"  {i}")

# 3. IDs que o JS atualiza mas NAO existem no HTML
faltando = set(ids_js) - set(ids_html)
print("\n=== IDs QUE O JS ATUALIZA MAS NAO EXISTEM NO HTML ===")
for i in sorted(faltando):
    print(f"  {i}")

# 4. IDs que existem no HTML mas o JS NAO atualiza
nao_usados = set(ids_html) - set(ids_js)
print("\n=== IDs NO HTML QUE O JS NAO ATUALIZA ===")
for i in sorted(nao_usados):
    if i.startswith("pdf-") or i.startswith("conc-"):
        print(f"  {i}")
