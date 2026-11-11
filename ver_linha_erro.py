p = 'pc_backend/main.py'
with open(p, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

print("=== Linhas 9770 a 9795 ===")
for i in range(9769, min(9795, len(linhas))):
    print(f"{i+1}: {linhas[i].rstrip()}")
