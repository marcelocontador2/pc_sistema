with open('script_1.js', 'r', encoding='utf-8') as f:
    linhas = f.readlines()

print(f"Total de linhas: {len(linhas)}")
print("\n=== PRIMEIRAS 20 LINHAS ===")
for i in range(min(20, len(linhas))):
    print(f"{i+1}: {linhas[i].rstrip()}")

print("\n=== ÚLTIMAS 20 LINHAS ===")
for i in range(max(0, len(linhas)-20), len(linhas)):
    print(f"{i+1}: {linhas[i].rstrip()}")
