with open(r"pc_backend\main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# início de _calc_liquidez
start = None
for i, l in enumerate(lines):
    if l.startswith("def _calc_liquidez"):
        start = i
        break

# próxima linha top-level (sem indentação, não vazia, não comentário)
end = len(lines)
for j in range(start + 1, len(lines)):
    s = lines[j]
    if s.strip() and not s[0].isspace() and not s.lstrip().startswith("#"):
        end = j
        break

print(f"=== _calc_liquidez COMPLETA (linhas {start+1}..{end}) ===")
for k in range(start, end):
    print(f"{k+1:5}: {lines[k]}", end="")

print("\n\n=== Últimas 30 linhas do main.py (onde inserir rotas) ===")
for k in range(max(0, len(lines)-30), len(lines)):
    print(f"{k+1:5}: {lines[k]}", end="")
