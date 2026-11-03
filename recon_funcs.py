import re
c = open(r"pc_frontend\conferencia_nova.html", encoding="utf-8-sig").read()
print("FUNÇÕES JAVASCRIPT ENCONTRADAS:")
for m in re.finditer(r'function\s+([a-zA-Z0-9_]+)\s*\(', c):
    print(" -", m.group(1))
