with open("pc_backend/main.py", "r", encoding="utf-8") as f:
    linhas = f.readlines()

print("=== Imports dos routers BF, Panorama e DVP ===")
print("=" * 80)
for i, linha in enumerate(linhas, 1):
    for termo in ["balanco_financeiro", "panorama", "bf_router", "panorama_router", "dvp_router", "dvp"]:
        if termo in linha and ("import" in linha or "include_router" in linha or "from" in linha):
            print(f"{i:>5}: {linha.rstrip()}")
            break

print()
print("=== Bloco de include_router (linhas 60-80) ===")
print("=" * 80)
for i in range(59, 80):
    print(f"{i+1:>5}: {linhas[i].rstrip()}")

print()
print("=== Bloco de include_router comentados (linhas 3760-3785) ===")
print("=" * 80)
for i in range(3759, min(3786, len(linhas))):
    print(f"{i+1:>5}: {linhas[i].rstrip()}")
