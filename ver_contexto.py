with open('script_1.js', 'r', encoding='utf-8') as f:
    linhas = f.readlines()

print("=== LINHAS 200 A 220 ===")
for i in range(199, min(220, len(linhas))):
    print(f"{i+1}: {linhas[i].rstrip()}")
