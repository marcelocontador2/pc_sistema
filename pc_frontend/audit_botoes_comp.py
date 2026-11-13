import re

with open("composicao_receitas_despesas.html", "r", encoding="utf-8") as f:
    html = f.read()

print("=== BOTOES E ONCLICK ===")
for m in re.finditer(r'<button[^>]*onclick="([^"]*)"[^>]*>([^<]*)</button>', html):
    print(f"Botao: '{m.group(2).strip()}' -> {m.group(1)}")

print("\n=== FUNCOES ENCONTRADAS ===")
for m in re.finditer(r'(async\s+)?function\s+(\w+)\s*\(', html):
    print(f"- {m.group(2)}")

print("\n=== IDs DOS SELECTS ===")
for m in re.finditer(r'<select[^>]*id="([^"]+)"[^>]*>', html):
    print(f"- {m.group(1)}")

print("\n=== IDs DAS TABELAS ===")
for m in re.finditer(r'<table[^>]*id="([^"]+)"[^>]*>', html):
    print(f"- {m.group(1)}")

print("\n=== CHAMADAS FETCH ===")
for m in re.finditer(r'fetch\([\'"]([^\'"]+)', html):
    print(f"- {m.group(1)}")
