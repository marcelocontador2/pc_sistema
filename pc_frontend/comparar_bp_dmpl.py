import re

def extrair_estrutura(path):
    with open(path, "r", encoding="utf-8") as f:
        s = f.read()
    
    # Pega os IDs dos elementos
    ids = re.findall(r'id="([^"]+)"', s)
    
    # Pega os onclick dos botoes
    botoes = re.findall(r'<button[^>]*onclick="([^"]*)"[^>]*>([^<]*)</button>', s)
    
    # Pega os fetch
    fetches = re.findall(r"fetch\('([^']+)'", s)
    
    # Pega a classe do checkbox
    check_classe = re.findall(r'<input[^>]*type="checkbox"[^>]*class="([^"]*)"', s)
    
    return ids, botoes, fetches, check_classe

print("=" * 60)
print("AUDITORIA BP vs DMPL")
print("=" * 60)

ids_bp, botoes_bp, fetches_bp, check_bp = extrair_estrutura("analise_bp.html")
ids_dmpl, botoes_dmpl, fetches_dmpl, check_dmpl = extrair_estrutura("analise_dmpl.html")

print("\n--- IDs no BP ---")
print(ids_bp[:10])

print("\n--- IDs no DMPL ---")
print(ids_dmpl[:10])

print("\n--- BOTOES NO BP ---")
for b in botoes_bp:
    print(f"  '{b[1]}' -> {b[0]}")

print("\n--- BOTOES NO DMPL ---")
for b in botoes_dmpl:
    print(f"  '{b[1]}' -> {b[0]}")

print("\n--- FETCHES NO BP ---")
print(fetches_bp[:5])

print("\n--- FETCHES NO DMPL ---")
print(fetches_dmpl[:5])

print("\n--- CLASSE DO CHECKBOX NO BP ---")
print(check_bp[:3])

print("\n--- CLASSE DO CHECKBOX NO DMPL ---")
print(check_dmpl[:3])
