import re

with open("pc_backend/main.py", "r", encoding="utf-8") as f:
    linhas = f.readlines()

print("=== TODAS as decoracoes @app no main.py ===")
print(f"{'Linha':>6} {'Ativa':<6} {'Metodo':<7} {'Rota':<60}")
print("-" * 100)

ativas = 0
comentadas = 0

for i, linha in enumerate(linhas, 1):
    # Verificar se a linha tem @app em qualquer lugar
    if "@app." in linha:
        # Verificar se e uma decoracao valida (comeca com @app, sem # antes)
        stripped = linha.lstrip()
        if stripped.startswith("@app."):
            ativa = "SIM"
            ativas += 1
        else:
            ativa = "COM#"
            comentadas += 1
        
        # Extrair metodo e rota
        m = re.search(r'@app\.(get|post|put|delete)\("([^"]+)"', linha)
        if m:
            metodo = m.group(1).upper()
            rota = m.group(2)
        else:
            metodo = "?"
            rota = "?"
        
        print(f"{i:>6} {ativa:<6} {metodo:<7} {rota:<60}")

print()
print(f"Total de @app: {ativas + comentadas} (ativas: {ativas}, comentadas: {comentadas})")
